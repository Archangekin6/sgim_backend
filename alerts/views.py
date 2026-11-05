from django.utils import timezone
from rest_framework import serializers, viewsets, status as http_status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter, OpenApiResponse, extend_schema, extend_schema_view, inline_serializer,
)

from partners.models import Partner
from .filters import AlertFilter
from .models import Alert, AlertHistory
from .serializers import (
    AlertDetailSerializer, AlertListSerializer,
    ChangeStatusSerializer, TransmitSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="Lister les alertes",
        description="Liste paginée. Filtres : status, priority, alert_type, center, channel, "
                    "call_time_after, call_time_before. Recherche : search. Tri : sort.",
    ),
    create=extend_schema(
        summary="Créer une alerte",
        description=(
            "Formulaire « Nouvelle Alerte ».\n\n"
            "Champs obligatoires : `call_time`, `channel` (canal de réception — UUID de AlertSource), "
            "`alert_type` (type d'incident — UUID de IncidentCategory), `description`, `operator_signature`.\n\n"
            "Champs optionnels : `priority` (UUID de Priority), `latitude`, `longitude`.\n\n"
            "Champs auto-générés par le serveur : `number` (ex: ALT-ABJ-2026-0001), `status` (NEW), `created_by`.\n\n"
            "Si `center` est omis, le centre du compte connecté est utilisé.\n\n"
            "Le partenaire notifié (`notified_partner`) se renseigne uniquement via `POST /{id}/transmit/`."
        ),
    ),
    retrieve=extend_schema(summary="Détail d'une alerte (personnes et historique inclus)"),
    update=extend_schema(summary="Remplacer une alerte"),
    partial_update=extend_schema(summary="Modifier partiellement une alerte"),
    destroy=extend_schema(summary="Supprimer une alerte"),
)
class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.select_related(
        "center", "channel", "alert_type", "priority", "created_by", "notified_partner"
    ).prefetch_related("history").all()
    permission_classes = [IsAuthenticated]
    filterset_class = AlertFilter
    ordering_fields = ["call_time", "created_at", "status", "number", "priority__level"]
    search_fields = ["number", "description", "operator_signature"]
    
    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_admin_tier:
            return qs
        # Chef de quart : voit uniquement les alertes de son quart (filtré par team sur operator_signature n'existe pas,
        # donc on filtre par centre + on laisse le frontend filtrer par quart via ?team=)
        if user.is_team_leader:
            return qs.filter(center_id=user.center_id) if user.center_id else qs.none()
        # Opérateur : voit les alertes de son centre
        return qs.filter(center_id=user.center_id) if user.center_id else qs.none()

    def get_permissions(self):
        """
        - Lecture seule : opérateurs, chefs de quart, admins
        - Écriture (create/update/delete/transmit/change_status) : opérateurs et admins uniquement
        """
        user = self.request.user
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        # Chef de quart : lecture seule — refus sur toute écriture
        if hasattr(user, 'is_team_leader') and user.is_authenticated and user.is_team_leader:
            from rest_framework.permissions import BasePermission
            class Deny(BasePermission):
                def has_permission(self, request, view):
                    return False
            return [Deny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "list":
            return AlertListSerializer
        return AlertDetailSerializer

    @extend_schema(
        summary="Changer le statut d'une alerte",
        description="Fait avancer l'alerte et enregistre la transition dans l'historique.",
        request=ChangeStatusSerializer,
        responses=AlertDetailSerializer,
    )
    @action(detail=True, methods=["post"])
    def change_status(self, request, pk=None):
        alert = self.get_object()
        serializer = ChangeStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        old_status = alert.status
        alert.status = serializer.validated_data["status"]
        alert.save(update_fields=["status", "updated_at"])

        AlertHistory.objects.create(
            alert=alert, old_status=old_status, new_status=alert.status,
            user=request.user, comment=serializer.validated_data.get("comment", ""),
        )
        alert = self.get_queryset().get(pk=alert.pk)  # recharge sans le cache prefetch obsolète
        return Response(AlertDetailSerializer(alert).data)

    @extend_schema(
        summary="Transmettre une alerte à un partenaire",
        description=(
            "Enregistre le partenaire notifié, l'heure exacte de transmission (valeur légale) "
            "et envoie automatiquement un **email au partenaire** avec les détails complets de l'alerte.\n\n"
            "**Payload :**\n"
            "- `partner` (UUID, obligatoire) : identifiant du partenaire à notifier — "
            "récupérer la liste via `GET /api/coordination/`.\n"
            "- `comment` (texte, optionnel) : message de transmission libre, inclus dans l'email "
            "et enregistré dans l'historique de l'alerte.\n\n"
            "**Réponse :**\n"
            "- `200` : alerte mise à jour. Si l'email a échoué, un champ `email_warning` est présent "
            "dans la réponse (la transmission en base reste valide).\n"
            "- `400` : partenaire inconnu.\n\n"
            "**Note :** si le partenaire n'a pas d'adresse email configurée, "
            "la transmission en base est effectuée sans envoi d'email."
        ),
        request=TransmitSerializer,
        responses={
            200: AlertDetailSerializer,
            400: OpenApiResponse(description="Partenaire inconnu."),
        },
    )
    @action(detail=True, methods=["post"])
    def transmit(self, request, pk=None):
        alert = self.get_object()
        serializer = TransmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            partner = Partner.objects.get(pk=serializer.validated_data["partner"])
        except Partner.DoesNotExist:
            return Response({"detail": "Partenaire inconnu."}, status=http_status.HTTP_400_BAD_REQUEST)

        comment = serializer.validated_data.get("comment", "")

        old_status = alert.status
        alert.notified_partner = partner
        alert.notified_at = timezone.now()
        alert.status = Alert.Status.TRANSMITTED
        alert.save()

        AlertHistory.objects.create(
            alert=alert, old_status=old_status, new_status=alert.status,
            user=request.user, comment=comment or f"Transmis à {partner.name}",
        )

        # ── Envoi email au partenaire ─────────────────────────────────────
        if partner.email:
            from django.template.loader import render_to_string
            ctx = {
                "alert": alert,
                "partner": partner,
                "transmitted_at": alert.notified_at,
                "operator": request.user.get_full_name() or request.user.username,
                "comment": comment,
            }
            subject = render_to_string("alerts/email_transmit_subject.txt", ctx).strip()
            body = render_to_string("alerts/email_transmit_body.txt", ctx)
            try:
                from django.core.mail import send_mail
                send_mail(
                    subject=subject,
                    message=body,
                    from_email=None,   # utilise DEFAULT_FROM_EMAIL
                    recipient_list=[partner.email],
                    fail_silently=False,
                )
            except Exception as exc:
                # L'alerte est déjà transmise en base — on ne bloque pas la réponse,
                # mais on informe le frontend que l'email a échoué.
                alert = self.get_queryset().get(pk=alert.pk)
                data = AlertDetailSerializer(alert).data
                data["email_warning"] = f"Alerte transmise, mais l'email n'a pas pu être envoyé : {exc}"
                return Response(data, status=http_status.HTTP_200_OK)

        alert = self.get_queryset().get(pk=alert.pk)
        return Response(AlertDetailSerializer(alert).data)


class HeatmapView(APIView):
    """
    Renvoie uniquement les positions des alertes (lat/lon) pour que le
    frontend construise la carte de densité (§5 spec v2 : carte
    thermique / points de chaleur, à la place du trafic temps réel).

    GET /api/alerts/heatmap/?period=90 (jours, défaut 90)
    GET /api/alerts/heatmap/?center=<id> (optionnel)
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["alerts"],
        summary="Positions des alertes (carte de densité)",
        description="Renvoie latitude/longitude des alertes situées géographiquement, pour construire une carte thermique côté frontend.",
        parameters=[
            OpenApiParameter("period", OpenApiTypes.INT, description="Nombre de jours en arrière (défaut 90)."),
            OpenApiParameter("center", OpenApiTypes.STR, description="ID du centre pour filtrer."),
        ],
        responses=inline_serializer(
            name="HeatmapResponse",
            fields={
                "count": serializers.IntegerField(),
                "points": inline_serializer(
                    name="HeatmapPoint",
                    fields={
                        "latitude": serializers.DecimalField(max_digits=9, decimal_places=6),
                        "longitude": serializers.DecimalField(max_digits=9, decimal_places=6),
                        "category__name": serializers.CharField(),
                        "number": serializers.CharField(),
                    },
                    many=True,
                ),
            },
        ),
    )
    def get(self, request):
        days = int(request.query_params.get("period", 90))
        since = timezone.now() - timezone.timedelta(days=days)

        qs = Alert.objects.filter(
            call_time__gte=since,
            latitude__isnull=False,
            longitude__isnull=False,
        )
        center_id = request.query_params.get("center")
        if center_id:
            qs = qs.filter(center_id=center_id)

        points = list(qs.values("latitude", "longitude", "alert_type__name", "number"))
        return Response({"count": len(points), "points": points})