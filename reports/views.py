from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import DailyReport
from .serializers import DailyReportSerializer

from django.db.models import Count
from django.utils import timezone
from rest_framework.views import APIView

from alerts.models import Alert
from sar.models import MeansEngagement



class DailyReportViewSet(viewsets.ModelViewSet):
    queryset = DailyReport.objects.select_related("center", "created_by", "validated_by").all()
    serializer_class = DailyReportSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["center", "team", "is_validated"]

    @action(detail=True, methods=["post"])
    def validate(self, request, pk=None):
        """Validation par le chef de quart -> déclenche l'envoi email (§6 spec v2)."""
        report = self.get_object()
        report.is_validated = True
        report.validated_by = request.user
        report.validated_at = timezone.now()
        report.save()

        try:
            send_mail(
                subject=f"Rapport de fin de journée - {report.center} - {report.report_date}",
                message=(
                    f"Équipe: {report.team}\n"
                    f"Alertes: {report.alerts_count} | Sauvetages: {report.rescues_count} | "
                    f"Coordinations: {report.coordinations_count} | Appels: {report.calls_received_count}\n\n"
                    f"{report.summary}"
                ),
                from_email=None,  # utilise DEFAULT_FROM_EMAIL
                recipient_list=["hierarchie@sgim.example"],  # à remplacer par la vraie adresse
                fail_silently=False,
            )
            report.email_sent = True
            report.save(update_fields=["email_sent"])
        except Exception as e:
            return Response(
                {"detail": f"Rapport validé mais email non envoyé: {e}", **DailyReportSerializer(report).data}
            )

        return Response(DailyReportSerializer(report).data)
    

class DashboardView(APIView):
    """
    Tableau de bord de pilotage consolidé (§1 spec v2) : cumul des
    assistances, sauvetages, coordinations, appels reçus. Optimisé
    pour une consultation simple côté mobile (JSON léger, agrégats
    déjà calculés côté serveur).

    GET /api/reports/dashboard/?period=7|30|90 (jours, défaut 30)
    GET /api/reports/dashboard/?center=<id> (optionnel)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        days = int(request.query_params.get("period", 30))
        since = timezone.now() - timezone.timedelta(days=days)
        center_id = request.query_params.get("center")

        alerts = Alert.objects.filter(call_time__gte=since)
        if center_id:
            alerts = alerts.filter(center_id=center_id)

        by_category = list(
            alerts.values("category__name").annotate(total=Count("id")).order_by("-total")
        )
        by_status = list(
            alerts.values("status").annotate(total=Count("id")).order_by("-total")
        )

        # "Coordinations" = alertes transmises à un partenaire (§1)
        coordinations_count = alerts.filter(notified_partner__isnull=False).count()
        # "Sauvetages" = moyens engagés sur des alertes de la période
        rescues_count = MeansEngagement.objects.filter(alert__in=alerts).count()

        return Response({
            "period_days": days,
            "alerts_total": alerts.count(),
            "alerts_new": alerts.filter(status=Alert.Status.NEW).count(),
            "alerts_qualified": alerts.filter(status=Alert.Status.QUALIFIED).count(),
            "coordinations_count": coordinations_count,
            "rescues_count": rescues_count,
            "calls_received_count": alerts.count(),  # chaque alerte = 1 appel reçu à l'origine
            "by_category": by_category,
            "by_status": by_status,
        })