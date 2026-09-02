from rest_framework import serializers
from .models import Vessel


class VesselSerializer(serializers.ModelSerializer):
    vessel_type_name = serializers.CharField(source="vessel_type.name", read_only=True, default=None)

    class Meta:
        model = Vessel
        fields = "__all__"