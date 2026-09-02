import uuid
from django.conf import settings
from django.db import models

from centers.models import Center
from alerts.models import Alert
from partners.models import Partner
from references.models import MeansType


class Means(models.Model):
    class Availability(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Disponible"
        ENGAGED = "ENGAGED", "Engagé"
        UNAVAILABLE = "UNAVAILABLE", "Indisponible / maintenance"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    means_type = models.ForeignKey(MeansType, on_delete=models.PROTECT, related_name="means")
    center = models.ForeignKey(Center, on_delete=models.SET_NULL, null=True, blank=True, related_name="means")
    partner = models.ForeignKey(Partner, on_delete=models.SET_NULL, null=True, blank=True, related_name="means")
    registration = models.CharField(max_length=50, blank=True)
    availability = models.CharField(max_length=20, choices=Availability.choices, default=Availability.AVAILABLE)
    home_base = models.CharField(max_length=150, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Means"

    def __str__(self):
        return f"{self.name} ({self.means_type})"


class MeansEngagement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name="engagements")
    means = models.ForeignKey(Means, on_delete=models.PROTECT, related_name="engagements")
    engaged_at = models.DateTimeField(auto_now_add=True)
    released_at = models.DateTimeField(null=True, blank=True)
    mission_role = models.CharField(max_length=200, blank=True)
    engaged_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="+")
    report = models.TextField(blank=True)

    class Meta:
        ordering = ["-engaged_at"]

    def __str__(self):
        return f"{self.means} sur {self.alert.number}"