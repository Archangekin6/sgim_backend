from rest_framework import serializers
from .models import DailyReport


class DailyReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyReport
        fields = "__all__"
        read_only_fields = [
            "id", "created_by", "created_at", "updated_at",
            "is_validated", "validated_by", "validated_at", "email_sent",
        ]

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)