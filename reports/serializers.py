from rest_framework import serializers
from .models import DailyReport


class DailyReportSerializer(serializers.ModelSerializer):
    # Champs affichés en lecture seule calculés côté serveur
    center_name = serializers.CharField(source="center.name", read_only=True)
    validated_by_name = serializers.CharField(
        source="validated_by.get_full_name", read_only=True, default=None
    )

    class Meta:
        model = DailyReport
        fields = [
            "id",
            # Identifiants du quart (auto-remplis à la création)
            "center", "center_name", "team", "report_date",
            # Contenu rédigé par l'agent
            "summary",
            # Compteurs calculés automatiquement
            "alerts_count", "coordinations_count",
            # Validation
            "is_validated", "validated_by", "validated_by_name", "validated_at", "email_sent",
            # Métadonnées
            "created_by", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id",
            # Auto-injectés depuis le compte de l'agent
            "center", "team",
            # Calculés automatiquement depuis les alertes/coordinations
            "alerts_count", "coordinations_count",
            # Validation
            "is_validated", "validated_by", "validated_at", "email_sent",
            # Métadonnées
            "created_by", "created_at", "updated_at",
        ]
