import uuid
from django.conf import settings
from django.db import models, transaction
from django.utils import timezone

from centers.models import Center
from vessels.models import Vessel
from partners.models import Partner
from references.models import AlertSource, IncidentCategory, Priority, Severity


def generate_alert_number(center_code: str) -> str:
    """Numéro unique lisible, calculé côté serveur uniquement (ex: ALT-ABJ-2026-0001)."""
    year = timezone.now().year
    prefix = f"ALT-{center_code}-{year}-"
    last = (
        Alert.objects.select_for_update()
        .filter(number__startswith=prefix)
        .order_by("-number")
        .first()
    )
    last_seq = int(last.number.rsplit("-", 1)[-1]) if last else 0
    return f"{prefix}{last_seq + 1:04d}"


class Alert(models.Model):
    class Status(models.TextChoices):
        NEW = "NEW", "Nouvelle"
        QUALIFIED = "QUALIFIED", "Qualifiée"
        TRANSMITTED = "TRANSMITTED", "Transmise au partenaire"
        CLOSED = "CLOSED", "Clôturée"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    number = models.CharField(max_length=30, unique=True, editable=False)
    center = models.ForeignKey(Center, on_delete=models.PROTECT, related_name="alerts")

    call_time = models.DateTimeField(help_text="Heure exacte de l'appel/signalement")
    channel = models.ForeignKey(AlertSource, on_delete=models.PROTECT, related_name="alerts")
    category = models.ForeignKey(IncidentCategory, on_delete=models.PROTECT, related_name="alerts")
    priority = models.ForeignKey(Priority, on_delete=models.SET_NULL, null=True, blank=True, related_name="alerts")
    severity = models.ForeignKey(Severity, on_delete=models.SET_NULL, null=True, blank=True, related_name="alerts")

    vessel = models.ForeignKey(Vessel, on_delete=models.SET_NULL, null=True, blank=True, related_name="alerts")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    position_text = models.CharField(max_length=200, blank=True)

    description = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)

    operator_signature = models.CharField(
        max_length=100, help_text="Nom de famille de l'opérateur (saisie manuelle obligatoire)"
    )

    notified_partner = models.ForeignKey(
        Partner, on_delete=models.SET_NULL, null=True, blank=True, related_name="alerts_notified"
    )
    notified_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="alerts_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-call_time"]
        indexes = [models.Index(fields=["status"]), models.Index(fields=["call_time"])]

    def __str__(self):
        return f"{self.number} - {self.category}"

    def save(self, *args, **kwargs):
        if not self.number:
            with transaction.atomic():
                self.number = generate_alert_number(self.center.code)
        super().save(*args, **kwargs)


class AlertHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name="history")
    old_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="+")
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.alert.number}: {self.old_status} -> {self.new_status}"


class AlertPerson(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name="involved_people")
    name = models.CharField(max_length=150, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    is_victim = models.BooleanField(default=False)
    status_note = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name or f"Personne #{self.pk}"