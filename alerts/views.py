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
        description="Liste paginée. Filtres : status, priority, category, center, channel, vessel, "
                    "call_time_after, call_time_before. Recherche : search. Tri : sort.",
    ),
    create=extend_schema(
        summary="Créer une alerte",
        description="Formulaire « Nouvelle Alerte ». Les champs channel, category, priority, severity "
                    "attendent l'UUID de la liste déroulante. Le numéro, le statut NEW et le créateur sont "
                    "générés par le serveur. Si `center` est omis, le centre du compte connecté est utilisé.",
    ),
    retrieve=extend_schema(summary="Détail d'une alerte (personnes et historique inclus)"),
    update=extend_schema(summary="Remplacer une alerte"),
    partial_update=extend_schema(summary="Modifier partiellement une alerte"),
    destroy=extend_schema(summary="Supprimer une alerte"),
)
class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.select_related(
        "center", "channel", "category", "priority", "severity", "vessel", "created_by", "notified_partner"
    ).prefetch_related("involved_people", "history").all()
    permission_classes = [IsAuthenticated]
    filterset_class = AlertFilter
    ordering_fields = ["call_time", "created_at", "status", "number", "priority__level"]
    search_fields = ["number", "description", "operator_signature"]

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
        description="Enregistre le partenaire notifié et l'heure exacte de transmission (valeur légale).",
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

        old_status = alert.status
        alert.notified_partner = partner
        alert.notified_at = timezone.now()
        alert.status = Alert.Status.TRANSMITTED
        alert.save()

        AlertHistory.objects.create(
            alert=alert, old_status=old_status, new_status=alert.status,
            user=request.user, comment=serializer.validated_data.get("comment", f"Transmis à {partner.name}"),
        )
        alert = self.get_queryset().get(pk=alert.pk)  # recharge sans le cache prefetch obsolète
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

        points = list(qs.values("latitude", "longitude", "category__name", "number"))
        return Response({"count": len(points), "points": points})