from rest_framework import serializers
from .models import Partner


class PartnerSerializer(serializers.ModelSerializer):
    partner_type_name = serializers.CharField(source="partner_type.name", read_only=True)

    class Meta:
        model = Partner
        fields = "__all__"