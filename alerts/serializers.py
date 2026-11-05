from rest_framework import serializers
from .models import Alert, AlertHistory


class AlertHistorySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.get_full_name", read_only=True, default=None)

    class Meta:
        model = AlertHistory
        fields = ["id", "old_status", "new_status", "user", "user_name", "comment", "created_at"]
        read_only_fields = fields


class AlertListSerializer(serializers.ModelSerializer):
    alert_type_name = serializers.CharField(source="alert_type.name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Alert
        fields = [
            "id", "number", "center", "alert_type", "alert_type_name", "priority",
            "status", "status_display", "call_time", "operator_signature",
        ]


class AlertDetailSerializer(serializers.ModelSerializer):
    history = AlertHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Alert
        fields = [
            "id", "number", "center", "call_time", "channel", "alert_type",
            "priority", "latitude", "longitude",
            "description", "status", "operator_signature",
            "notified_partner", "notified_at",
            "history",
            "created_by", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "number", "status", "created_by", "created_at", "updated_at",
            # notified_partner et notified_at gérés exclusivement via /transmit/
            "notified_partner", "notified_at",
        ]
        extra_kwargs = {
            "center": {"required": False},
        }

    def create(self, validated_data):
        request_user = self.context["request"].user

        center = validated_data.get("center") or request_user.center
        if not center:
            raise serializers.ValidationError({
                "center": "Impossible de créer une alerte : aucun centre n'est associé à ce compte. Contactez un administrateur."
            })
        validated_data["center"] = center
        validated_data["created_by"] = request_user

        return Alert.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ChangeStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Alert.Status.choices)
    comment = serializers.CharField(required=False, allow_blank=True)


class TransmitSerializer(serializers.Serializer):
    partner = serializers.UUIDField()
    comment = serializers.CharField(required=False, allow_blank=True)
