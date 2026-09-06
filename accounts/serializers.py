from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User
from .models import PasswordResetRequest


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


class PasswordResetRequestCreateSerializer(serializers.Serializer):
    """Utilisé par l'utilisateur qui a oublié son mot de passe (pas besoin d'être connecté)."""
    username = serializers.CharField()
    note = serializers.CharField(required=False, allow_blank=True)

    def validate_username(self, value):
        if not User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Aucun compte avec cet identifiant.")
        return value


class PasswordResetRequestSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    resolved_by_username = serializers.CharField(source="resolved_by.username", read_only=True, default=None)

    class Meta:
        model = PasswordResetRequest
        fields = [
            "id", "user", "username", "note", "status",
            "requested_at", "resolved_by", "resolved_by_username", "resolved_at",
        ]
        read_only_fields = fields


class ResolvePasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, validators=[validate_password])


class BulkResolveItemSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    new_password = serializers.CharField(write_only=True, validators=[validate_password])


class BulkResolveSerializer(serializers.Serializer):
    items = BulkResolveItemSerializer(many=True)