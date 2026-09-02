from rest_framework import serializers
from . import models


class ReferenceSerializerBase(serializers.ModelSerializer):
    class Meta:
        fields = ["id", "code", "name", "order", "is_active"]


class AlertSourceSerializer(ReferenceSerializerBase):
    class Meta(ReferenceSerializerBase.Meta):
        model = models.AlertSource


class PrioritySerializer(ReferenceSerializerBase):
    class Meta(ReferenceSerializerBase.Meta):
        model = models.Priority
        fields = ReferenceSerializerBase.Meta.fields + ["level"]


class SeveritySerializer(ReferenceSerializerBase):
    class Meta(ReferenceSerializerBase.Meta):
        model = models.Severity
        fields = ReferenceSerializerBase.Meta.fields + ["level"]


class VesselTypeSerializer(ReferenceSerializerBase):
    class Meta(ReferenceSerializerBase.Meta):
        model = models.VesselType


class IncidentCategorySerializer(ReferenceSerializerBase):
    class Meta(ReferenceSerializerBase.Meta):
        model = models.IncidentCategory


class MeansCategorySerializer(ReferenceSerializerBase):
    class Meta(ReferenceSerializerBase.Meta):
        model = models.MeansCategory


class MeansTypeSerializer(ReferenceSerializerBase):
    class Meta(ReferenceSerializerBase.Meta):
        model = models.MeansType
        fields = ReferenceSerializerBase.Meta.fields + ["category"]


class PartnerTypeSerializer(ReferenceSerializerBase):
    class Meta(ReferenceSerializerBase.Meta):
        model = models.PartnerType


class PersonRoleSerializer(ReferenceSerializerBase):
    class Meta(ReferenceSerializerBase.Meta):
        model = models.PersonRole


class PersonStatusSerializer(ReferenceSerializerBase):
    class Meta(ReferenceSerializerBase.Meta):
        model = models.PersonStatus