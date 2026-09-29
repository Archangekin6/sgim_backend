from rest_framework import serializers


class TotalByCategorySerializer(serializers.Serializer):
    category__name = serializers.CharField()
    total = serializers.IntegerField()


class TotalByCenterSerializer(serializers.Serializer):
    center__name = serializers.CharField()
    total = serializers.IntegerField()


class TotalByTypeSerializer(serializers.Serializer):
    means_type__name = serializers.CharField()
    total = serializers.IntegerField()


class AlertsTodaySerializer(serializers.Serializer):
    date = serializers.DateField()
    count = serializers.IntegerField()
    by_status = serializers.DictField(child=serializers.IntegerField(), help_text='Ex : {"NEW": 3, "QUALIFIED": 1}')
    by_category = TotalByCategorySerializer(many=True)


class IncidentsOpenSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    high_priority_count = serializers.IntegerField()
    by_status = serializers.DictField(child=serializers.IntegerField())
    by_category = TotalByCategorySerializer(many=True)


class PersonnelAvailableSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    available = serializers.IntegerField()
    engaged = serializers.IntegerField()
    unavailable = serializers.IntegerField()
    available_by_type = TotalByTypeSerializer(many=True)


class StatsByRoleSerializer(serializers.Serializer):
    role = serializers.CharField()
    scope = serializers.ChoiceField(choices=["center", "global"])
    alerts_today = serializers.IntegerField()
    alerts_open = serializers.IntegerField()
    alerts_by_status = serializers.DictField(child=serializers.IntegerField())
    team = serializers.CharField(required=False, help_text="Opérateur uniquement.")
    daily_report_submitted_today = serializers.BooleanField(required=False, help_text="Opérateur uniquement.")
    alerts_last_30_days = serializers.IntegerField(required=False, help_text="Admin et Super Admin.")
    alerts_by_center = TotalByCenterSerializer(many=True, required=False, help_text="Admin et Super Admin.")
    daily_reports_pending_validation = serializers.IntegerField(required=False, help_text="Admin et Super Admin.")
    means_available = serializers.IntegerField(required=False, help_text="Admin et Super Admin.")
    pending_password_resets = serializers.IntegerField(required=False, help_text="Super Admin uniquement.")
    active_users = serializers.IntegerField(required=False, help_text="Super Admin uniquement.")