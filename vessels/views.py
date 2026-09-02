from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Vessel
from .serializers import VesselSerializer


class VesselViewSet(viewsets.ModelViewSet):
    queryset = Vessel.objects.select_related("vessel_type").all()
    serializer_class = VesselSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["vessel_type", "flag"]
    search_fields = ["name", "mmsi", "imo"]