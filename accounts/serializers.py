from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    center_name = serializers.CharField(source="center.name", read_only=True, default=None)
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])

    class Meta:
        model = User
        fields = [
            "id", "username", "first_name", "last_name", "email", "role", "team",
            "center", "center_name", "phone", "is_active", "password",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class MeSerializer(serializers.ModelSerializer):
    """Profil du compte connecté - utile pour que le front sache qui est
    connecté (Car 1, Car 2... ou Admin) et pré-remplisse le centre (§3 spec v2)."""
    center_name = serializers.CharField(source="center.name", read_only=True, default=None)

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "role", "team", "center", "center_name"]