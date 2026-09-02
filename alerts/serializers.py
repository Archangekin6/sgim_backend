from rest_framework import serializers
from .models import Alert, AlertHistory, AlertPerson


class AlertPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertPerson
        fields = ["id", "name", "nationality", "is_victim", "status_note"]
        read_only_fields = ["id"]


class AlertHistorySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.get_full_name", read_only=True, default=None)

    class Meta:
        model = AlertHistory
        fields = ["id", "old_status", "new_status", "user", "user_name", "comment", "created_at"]
        read_only_fields = fields


class AlertListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Alert
        fields = [
            "id", "number", "center", "category", "category_name", "priority",
            "status", "status_display", "call_time", "operator_signature",
        ]


class AlertDetailSerializer(serializers.ModelSerializer):
    involved_people = AlertPersonSerializer(many=True, required=False)
    history = AlertHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Alert
        fields = [
            "id", "number", "center", "call_time", "channel", "category",
            "priority", "severity", "vessel", "latitude", "longitude", "position_text",
            "description", "status", "operator_signature",
            "notified_partner", "notified_at",
            "involved_people", "history",
            "created_by", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "number", "status", "created_by", "created_at", "updated_at"]

    def create(self, validated_data):
        people_data = validated_data.pop("involved_people", [])
        request_user = self.context["request"].user
        validated_data["created_by"] = request_user
        if not validated_data.get("center"):
            validated_data["center"] = request_user.center
        alert = Alert.objects.create(**validated_data)
        for person_data in people_data:
            AlertPerson.objects.create(alert=alert, **person_data)
        return alert

    def update(self, instance, validated_data):
        people_data = validated_data.pop("involved_people", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if people_data is not None:
            instance.involved_people.all().delete()
            for person_data in people_data:
                AlertPerson.objects.create(alert=instance, **person_data)
        return instance


class ChangeStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Alert.Status.choices)
    comment = serializers.CharField(required=False, allow_blank=True)


class TransmitSerializer(serializers.Serializer):
    partner = serializers.UUIDField()
    comment = serializers.CharField(required=False, allow_blank=True)