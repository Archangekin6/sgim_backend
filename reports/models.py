import uuid
from django.conf import settings
from django.db import models

from centers.models import Center


class DailyReport(models.Model):
    """
    Rapport de fin de journée (§6 spec v2). Rédigé par le chef de quart,
    synthétise les 24h de service. À la validation, un email est envoyé
    automatiquement à la hiérarchie (adresse configurée dans le système).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    center = models.ForeignKey(Center, on_delete=models.PROTECT, related_name="daily_reports")
    report_date = models.DateField()
    team = models.CharField(max_length=20, help_text="Quart ayant rédigé le rapport (Car1-4/MRSC)")

    summary = models.TextField(help_text="Synthèse des événements des dernières 24h")
    alerts_count = models.PositiveIntegerField(default=0)
    rescues_count = models.PositiveIntegerField(default=0)
    coordinations_count = models.PositiveIntegerField(default=0)
    calls_received_count = models.PositiveIntegerField(default=0)

    is_validated = models.BooleanField(default=False)
    validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    validated_at = models.DateTimeField(null=True, blank=True)
    email_sent = models.BooleanField(default=False)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="daily_reports_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-report_date"]
        unique_together = ["center", "report_date", "team"]

    def __str__(self):
        return f"{self.center} - {self.team} - {self.report_date}"