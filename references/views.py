from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from . import models, serializers


class ReferenceViewSetBase(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = self.queryset
        if self.request.query_params.get("include_inactive") != "true":
            qs = qs.filter(is_active=True)
        return qs


class AlertSourceViewSet(ReferenceViewSetBase):
    queryset = models.AlertSource.objects.all()
    serializer_class = serializers.AlertSourceSerializer


class PriorityViewSet(ReferenceViewSetBase):
    queryset = models.Priority.objects.all()
    serializer_class = serializers.PrioritySerializer


class SeverityViewSet(ReferenceViewSetBase):
    queryset = models.Severity.objects.all()
    serializer_class = serializers.SeveritySerializer


class VesselTypeViewSet(ReferenceViewSetBase):
    queryset = models.VesselType.objects.all()
    serializer_class = serializers.VesselTypeSerializer


class IncidentCategoryViewSet(ReferenceViewSetBase):
    queryset = models.IncidentCategory.objects.all()
    serializer_class = serializers.IncidentCategorySerializer


class MeansCategoryViewSet(ReferenceViewSetBase):
    queryset = models.MeansCategory.objects.all()
    serializer_class = serializers.MeansCategorySerializer


class MeansTypeViewSet(ReferenceViewSetBase):
    queryset = models.MeansType.objects.select_related("category").all()
    serializer_class = serializers.MeansTypeSerializer
    filterset_fields = ["category"]


class PartnerTypeViewSet(ReferenceViewSetBase):
    queryset = models.PartnerType.objects.all()
    serializer_class = serializers.PartnerTypeSerializer


class PersonRoleViewSet(ReferenceViewSetBase):
    queryset = models.PersonRole.objects.all()
    serializer_class = serializers.PersonRoleSerializer


class PersonStatusViewSet(ReferenceViewSetBase):
    queryset = models.PersonStatus.objects.all()
    serializer_class = serializers.PersonStatusSerializer