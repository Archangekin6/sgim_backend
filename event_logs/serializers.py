from rest_framework import serializers
from .models import EventLog


class EventLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.get_full_name", read_only=True, default=None)
    action_type_display = serializers.CharField(source="get_action_type_display", read_only=True)

    class Meta:
        model = EventLog
        fields = ["id", "timestamp", "user", "user_name", "action_type", "action_type_display", "description"]
        read_only_fields = fields