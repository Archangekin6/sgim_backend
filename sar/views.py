from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Means, MeansEngagement
from .serializers import MeansEngagementSerializer, MeansSerializer


class MeansViewSet(viewsets.ModelViewSet):
    queryset = Means.objects.select_related("means_type", "center", "partner").all()
    serializer_class = MeansSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["means_type", "availability", "center"]
    search_fields = ["name", "registration"]


class MeansEngagementViewSet(viewsets.ModelViewSet):
    queryset = MeansEngagement.objects.select_related("means", "alert").all()
    serializer_class = MeansEngagementSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["alert", "means"]