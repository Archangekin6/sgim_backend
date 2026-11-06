from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer

from alerts.models import Alert
from partners.models import Partner


# ── Serializers légers pour cet endpoint ─────────────────────────────────────

class ActiveAlertSerializer(serializers.ModelSerializer):
    alert_type_name = serializers.CharField(source="alert_type.name", read_only=True)
    center_name = serializers.CharField(source="center.name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Alert
        fields = [
            "id", "number", "call_time",
            "alert_type", "alert_type_name",
            "center", "center_name",
            "status", "status_display",
            "description", "operator_signature",
            "notified_partner", "notified_at",
        ]


class CoordinationPartnerSerializer(serializers.ModelSerializer):
    partner_type_name = serializers.CharField(source="partner_type.name", read_only=True)

    class Meta:
        model = Partner
        fields = ["id", "name", "partner_type", "partner_type_name", "phone", "email", "coverage_area"]


# ── Vue principale ────────────────────────────────────────────────────────────

@extend_schema(
    tags=["coordination"],
    summary="Données de l'onglet Coordination",
    description=(
        "Retourne en une seule requête :\n\n"
        "- **`active_alerts`** : alertes avec statut NEW, QUALIFIED ou TRANSMITTED, "
        "filtrées par centre pour les opérateurs.\n"
        "- **`partners`** : liste des partenaires actifs disponibles à notifier.\n\n"
        "**Pour transmettre une alerte**, utiliser "
        "`POST /api/alerts/{id}/transmit/` avec le payload suivant :\n"
        "```json\n"
        "{\n"
        "  \"partner\": \"<uuid_partenaire>\",\n"
        "  \"comment\": \"Message de transmission (optionnel)\"\n"
        "}\n"
        "```\n"
        "Le `comment` est enregistré dans l'historique de l'alerte."
    ),
    responses=inline_serializer(
        name="CoordinationResponse",
        fields={
            "active_alerts": ActiveAlertSerializer(many=True),
            "partners": CoordinationPartnerSerializer(many=True),
        },
    ),
)
class CoordinationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Chef de quart : accès interdit à la coordination
        if user.is_team_leader:
            return Response(
                {"detail": "Accès non autorisé. La coordination est réservée aux opérateurs et administrateurs."},
                status=403,
            )

        try:
            # Alertes actives (tout sauf CLOSED)
            active_statuses = [Alert.Status.NEW, Alert.Status.QUALIFIED, Alert.Status.TRANSMITTED]
            alerts_qs = (
                Alert.objects
                .select_related("alert_type", "center", "notified_partner")
                .filter(status__in=active_statuses)
            )
            # Les opérateurs ne voient que leur centre
            if not user.is_admin_tier:
                alerts_qs = alerts_qs.filter(center_id=user.center_id) if user.center_id else alerts_qs.none()

            # Partenaires actifs
            partners_qs = Partner.objects.select_related("partner_type").filter(is_active=True)

            return Response({
                "active_alerts": ActiveAlertSerializer(alerts_qs, many=True).data,
                "partners": CoordinationPartnerSerializer(partners_qs, many=True).data,
            })
        except Exception as exc:
            import traceback
            return Response(
                {"detail": str(exc), "trace": traceback.format_exc()},
                status=500,
            )
