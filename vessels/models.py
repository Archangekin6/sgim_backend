import uuid
from django.db import models
from references.models import VesselType


class Vessel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    vessel_type = models.ForeignKey(
        VesselType, on_delete=models.PROTECT, null=True, blank=True, related_name="vessels"
    )
    flag = models.CharField("Pavillon", max_length=100, blank=True)
    mmsi = models.CharField("MMSI", max_length=20, blank=True, db_index=True)
    imo = models.CharField("Numéro IMO", max_length=20, blank=True, db_index=True)
    call_sign = models.CharField(max_length=30, blank=True)
    owner = models.CharField(max_length=150, blank=True)
    crew_count = models.PositiveIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name