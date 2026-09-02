from rest_framework import serializers
from .models import Means, MeansEngagement


class MeansSerializer(serializers.ModelSerializer):
    means_type_name = serializers.CharField(source="means_type.name", read_only=True)

    class Meta:
        model = Means
        fields = "__all__"


class MeansEngagementSerializer(serializers.ModelSerializer):
    means_name = serializers.CharField(source="means.name", read_only=True)
    alert_number = serializers.CharField(source="alert.number", read_only=True)

    class Meta:
        model = MeansEngagement
        fields = "__all__"
        read_only_fields = ["engaged_by"]

    def create(self, validated_data):
        validated_data["engaged_by"] = self.context["request"].user
        means = validated_data["means"]
        means.availability = Means.Availability.ENGAGED
        means.save(update_fields=["availability"])
        return super().create(validated_data)