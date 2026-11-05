from django.core.mail import send_mail
from django.core.mail import send_mail
from django.db.models import Count, Q
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from alerts.models import Alert
from alerts.filters import AlertFilter
from accounts.permissions import IsAdminTier, IsTeamLeader
from sar.models import MeansEngagement

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter, OpenApiResponse, extend_schema, extend_schema_view, inline_serializer,
)

from .exports import build_alert_pdf, build_alerts_excel, build_daily_report_pdf
from .models import DailyReport
from .serializers import DailyReportSerializer


class _IsTeamLeaderOrAdmin(BasePermission):
    """Chef de quart ou admin — utilisé pour l'action validate et destroy."""
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and
            (getattr(user, 'is_team_leader', False) or getattr(user, 'is_admin_tier', False))
        )


# ─────────────────────────────────────────────────────────────────────────────
# Rapports journaliers
# ─────────────────────────────────────────────────────────────────────────────

@extend_schema_view(
    list=extend_schema(summary="Lister les rapports journaliers", tags=["reports"]),
    retrieve=extend_schema(summary="Détail d'un rapport journalier", tags=["reports"]),
    create=extend_schema(summary="Créer un rapport journalier", tags=["reports"]),
    update=extend_schema(summary="Remplacer un rapport journalier", tags=["reports"]),
    partial_update=extend_schema(summary="Modifier partiellement un rapport journalier", tags=["reports"]),
    destroy=extend_schema(summary="Supprimer un rapport journalier", tags=["reports"]),
)
class DailyReportViewSet(viewsets.ModelViewSet):
    queryset = DailyReport.objects.select_related("center", "created_by", "validated_by").all()
    serializer_class = DailyReportSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["center", "team", "is_validated"]

    def get_permissions(self):
        if self.action == "validate":
            return [_IsTeamLeaderOrAdmin()]
        if self.action == "destroy":
            return [IsAdminTier()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_admin_tier:
            return qs
        # Chef de quart : voit uniquement les rapports de son quart et son centre
        if user.is_team_leader:
            return qs.filter(center=user.center, team=user.team) if (user.team and user.center) else qs.none()
        # Opérateur : voit les rapports de son centre
        return qs.filter(center=user.center) if user.center else qs.none()

    def perform_create(self, serializer):
        user = self.request.user
        center = user.center
        team = user.team

        # Calcul automatique des compteurs sur les dernières 24h pour ce centre/quart
        from django.utils import timezone
        from alerts.models import Alert
        since = timezone.now() - timezone.timedelta(hours=24)

        # Alertes créées par des agents de ce centre dans les dernières 24h
        alerts_count = Alert.objects.filter(
            center=center,
            created_at__gte=since,
        ).count()

        # Coordinations = alertes transmises à un partenaire sur la même période
        coordinations_count = Alert.objects.filter(
            center=center,
            status=Alert.Status.TRANSMITTED,
            notified_at__gte=since,
        ).count()

        serializer.save(
            created_by=user,
            center=center,
            team=team,
            alerts_count=alerts_count,
            coordinations_count=coordinations_count,
        )

    @extend_schema(
        summary="Valider un rapport journalier",
        description="Marque le rapport comme validé et envoie un e-mail à la hiérarchie.",
        request=None,
        responses={200: DailyReportSerializer},
        tags=["reports"],
    )
    @action(detail=True, methods=["post"])
    def validate(self, request, pk=None):
        """Validation par le chef de quart -> déclenche l'envoi email."""
        report = self.get_object()

        # Un chef de quart ne peut valider que les rapports de son propre quart
        user = request.user
        if user.is_team_leader and (report.team != user.team or report.center != user.center):
            return Response(
                {"detail": "Vous ne pouvez valider que les rapports de votre quart."},
                status=status.HTTP_403_FORBIDDEN,
            )

        report.is_validated = True
        report.validated_by = request.user
        report.validated_at = timezone.now()
        report.save()

        try:
            send_mail(
                subject=f"Rapport de fin de journée - {report.center} - {report.report_date}",
                message=(
                    f"Équipe: {report.team}\n"
                    f"Alertes: {report.alerts_count} | "
                    f"Coordinations: {report.coordinations_count}\n\n"
                    f"{report.summary}"
                ),
                from_email=None,
                recipient_list=["hierarchie@sgim.example"],
                fail_silently=False,
            )
            report.email_sent = True
            report.save(update_fields=["email_sent"])
        except Exception as e:
            return Response(
                {"detail": f"Rapport validé mais email non envoyé: {e}", **DailyReportSerializer(report).data}
            )

        return Response(DailyReportSerializer(report).data)

    @extend_schema(
        summary="Télécharger le PDF d'un rapport journalier",
        description="Génère et retourne la fiche PDF du rapport (A4, mise en page officielle SGIM).",
        request=None,
        responses={200: OpenApiResponse(description="Fichier PDF (application/pdf)")},
        tags=["exports"],
    )
    @action(detail=True, methods=["get"], url_path="pdf")
    def pdf(self, request, pk=None):
        report = self.get_object()
        buf = build_daily_report_pdf(report)
        filename = f"rapport_{report.report_date}_{report.team}.pdf"
        response = HttpResponse(buf, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


# ─────────────────────────────────────────────────────────────────────────────
# Export PDF — Fiche d'alerte
# ─────────────────────────────────────────────────────────────────────────────

@extend_schema(
    tags=["exports"],
    summary="Télécharger le PDF d'une alerte",
    description=(
        "Génère la fiche complète d'une alerte au format PDF (A4) : "
        "informations générales, localisation, personnes impliquées, "
        "moyens engagés et historique des statuts."
    ),
    responses={
        200: OpenApiResponse(description="Fichier PDF (application/pdf)"),
        404: OpenApiResponse(description="Alerte introuvable."),
    },
)
class AlertPDFView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            alert = (
                Alert.objects
                .select_related(
                    "center", "channel", "alert_type", "priority", "severity",
                    "vessel", "created_by", "notified_partner",
                )
                .prefetch_related(
                    "involved_people",
                    "history__user",
                    "engagements__means",
                    "engagements__engaged_by",
                )
                .get(pk=pk)
            )
        except Alert.DoesNotExist:
            return Response({"detail": "Alerte introuvable."}, status=status.HTTP_404_NOT_FOUND)

        # Restriction centre pour les non-admins
        user = request.user
        if not user.is_admin_tier and str(alert.center_id) != str(user.center_id):
            return Response({"detail": "Accès refusé."}, status=status.HTTP_403_FORBIDDEN)

        buf = build_alert_pdf(alert)
        filename = f"alerte_{alert.number}.pdf"
        response = HttpResponse(buf, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


# ─────────────────────────────────────────────────────────────────────────────
# Export Excel — Liste des alertes
# ─────────────────────────────────────────────────────────────────────────────

@extend_schema(
    tags=["exports"],
    summary="Exporter les alertes en Excel (.xlsx)",
    description=(
        "Applique les mêmes filtres que `GET /api/alerts/` "
        "(status, category, priority, center, call_time_after, call_time_before, search) "
        "et retourne un fichier Excel avec toutes les colonnes.\n\n"
        "Les opérateurs ne voient que les alertes de leur centre."
    ),
    parameters=[
        OpenApiParameter("status", OpenApiTypes.STR, description="NEW, QUALIFIED, TRANSMITTED, CLOSED ou active."),
        OpenApiParameter("category", OpenApiTypes.STR, description="UUID, code ou nom de la catégorie."),
        OpenApiParameter("priority", OpenApiTypes.STR, description="UUID, code ou nom de la priorité."),
        OpenApiParameter("center", OpenApiTypes.STR, description="UUID du centre (admins uniquement)."),
        OpenApiParameter("call_time_after", OpenApiTypes.DATETIME, description="Date de début (ISO 8601)."),
        OpenApiParameter("call_time_before", OpenApiTypes.DATETIME, description="Date de fin (ISO 8601)."),
        OpenApiParameter("search", OpenApiTypes.STR, description="Recherche libre (numéro, description, opérateur)."),
    ],
    responses={
        200: OpenApiResponse(
            description="Fichier Excel (application/vnd.openxmlformats-officedocument.spreadsheetml.sheet)"
        ),
    },
)
class AlertExcelExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = (
            Alert.objects
            .select_related(
                "center", "channel", "category", "priority",
                "severity", "vessel", "created_by", "notified_partner",
            )
            .all()
        )

        # Restriction centre pour les non-admins (cohérence avec AlertViewSet)
        user = request.user
        if not user.is_admin_tier:
            qs = qs.filter(center_id=user.center_id) if user.center_id else qs.none()

        # Filtres via AlertFilter
        filterset = AlertFilter(request.GET, queryset=qs, request=request)
        if not filterset.is_valid():
            return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)
        qs = filterset.qs

        # Recherche libre
        search = request.query_params.get("search", "").strip()
        if search:
            qs = qs.filter(
                Q(number__icontains=search) |
                Q(description__icontains=search) |
                Q(operator_signature__icontains=search)
            )

        buf = build_alerts_excel(qs)
        filename = f"alertes_export_{timezone.now().strftime('%Y%m%d_%H%M')}.xlsx"
        content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        response = HttpResponse(buf, content_type=content_type)
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


# ─────────────────────────────────────────────────────────────────────────────
# Dashboard
# ─────────────────────────────────────────────────────────────────────────────

class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["reports"],
        summary="Tableau de bord global",
        description="Indicateurs agrégés sur alertes, coordinations et moyens, période réglable.",
        parameters=[
            OpenApiParameter("period", OpenApiTypes.INT, description="Nombre de jours en arrière (défaut 30)."),
            OpenApiParameter("center", OpenApiTypes.STR, description="ID du centre pour filtrer."),
        ],
        responses=inline_serializer(
            name="GlobalDashboardResponse",
            fields={
                "period_days": serializers.IntegerField(),
                "alerts_total": serializers.IntegerField(),
                "alerts_new": serializers.IntegerField(),
                "alerts_qualified": serializers.IntegerField(),
                "coordinations_count": serializers.IntegerField(),
                "rescues_count": serializers.IntegerField(),
                "calls_received_count": serializers.IntegerField(),
                "by_category": serializers.ListField(),
                "by_status": serializers.ListField(),
            },
        ),
    )
    def get(self, request):
        days = int(request.query_params.get("period", 30))
        since = timezone.now() - timezone.timedelta(days=days)
        center_id = request.query_params.get("center")

        alerts = Alert.objects.filter(call_time__gte=since)
        if center_id:
            alerts = alerts.filter(center_id=center_id)

        by_category = list(
            alerts.values("alert_type__name").annotate(total=Count("id")).order_by("-total")
        )
        by_status = list(
            alerts.values("status").annotate(total=Count("id")).order_by("-total")
        )

        coordinations_count = alerts.filter(notified_partner__isnull=False).count()
        rescues_count = MeansEngagement.objects.filter(alert__in=alerts).count()

        return Response({
            "period_days": days,
            "alerts_total": alerts.count(),
            "alerts_new": alerts.filter(status=Alert.Status.NEW).count(),
            "alerts_qualified": alerts.filter(status=Alert.Status.QUALIFIED).count(),
            "coordinations_count": coordinations_count,
            "rescues_count": rescues_count,
            "calls_received_count": alerts.count(),
            "by_category": by_category,
            "by_status": by_status,
        })


# ─────────────────────────────────────────────────────────────────────────────
# Logout
# ─────────────────────────────────────────────────────────────────────────────

class LogoutView(APIView):
    """
    Déconnexion : invalide le refresh token pour qu'il ne puisse plus
    être utilisé pour obtenir un nouvel access token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
        except (KeyError, TokenError):
            return Response(
                {"detail": "Refresh token manquant ou invalide."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"detail": "Déconnexion réussie."}, status=status.HTTP_205_RESET_CONTENT)
