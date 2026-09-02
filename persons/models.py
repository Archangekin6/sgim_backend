import uuid
from django.db import models

from alerts.models import Alert
from vessels.models import Vessel
from references.models import PersonRole, PersonStatus


class Person(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name="people")
    vessel = models.ForeignKey(Vessel, on_delete=models.SET_NULL, null=True, blank=True, related_name="people")

    name = models.CharField(max_length=150, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    sex = models.CharField(max_length=1, choices=[("M", "Masculin"), ("F", "Féminin")], blank=True)

    role = models.ForeignKey(PersonRole, on_delete=models.PROTECT, related_name="people")
    status = models.ForeignKey(PersonStatus, on_delete=models.PROTECT, related_name="people")

    status_note = models.TextField(blank=True)
    handled_by = models.CharField(max_length=200, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name or 'Anonyme'} ({self.role})"