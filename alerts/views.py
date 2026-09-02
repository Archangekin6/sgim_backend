from django.utils import timezone
from rest_framework import viewsets, status as http_status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from partners.models import Partner
from .models import Alert, AlertHistory
from .serializers import (
    AlertDetailSerializer, AlertListSerializer,
    ChangeStatusSerializer, TransmitSerializer,
)


class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.select_related(
        "center", "channel", "category", "priority", "severity", "vessel", "created_by", "notified_partner"
    ).prefetch_related("involved_people", "history").all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "center", "category", "priority"]
    search_fields = ["number", "description", "operator_signature"]
    ordering_fields = ["call_time", "created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return AlertListSerializer
        return AlertDetailSerializer

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
        return Response(AlertDetailSerializer(alert).data)

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
        return Response(AlertDetailSerializer(alert).data)