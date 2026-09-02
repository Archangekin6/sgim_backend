from rest_framework import serializers
from .models import Person


class PersonSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source="role.name", read_only=True)
    status_name = serializers.CharField(source="status.name", read_only=True)

    class Meta:
        model = Person
        fields = "__all__"