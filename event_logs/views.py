from rest_framework import viewsets
from accounts.permissions import IsAdminTier
from .models import EventLog
from .serializers import EventLogSerializer


class EventLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Lecture seule, réservé aux Admin/Super Admin (§5 spec v2)."""
    queryset = EventLog.objects.select_related("user").all()
    serializer_class = EventLogSerializer
    permission_classes = [IsAdminTier]
    filterset_fields = ["action_type", "user"]
    search_fields = ["description"]