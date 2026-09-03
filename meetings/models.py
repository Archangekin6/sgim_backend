import uuid
from django.conf import settings
from django.db import models


def attendance_sheet_path(instance, filename):
    return f"meetings/{instance.id}/attendance_{filename}"


class Meeting(models.Model):
    """
    Réunions de crise ou de planification, internes ou avec partenaires
    externes (§6 spec v2). Compte-rendu texte + fiche de présence
    scannée (PDF) obligatoirement jointe.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    meeting_date = models.DateField()
    minutes = models.TextField(help_text="Compte-rendu de la réunion (texte libre ou collé)")

    attendance_sheet = models.FileField(
        upload_to=attendance_sheet_path,
        help_text="Fiche de présence scannée (PDF) avec signatures manuscrites",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="meetings_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-meeting_date"]

    def __str__(self):
        return f"{self.title} - {self.meeting_date}"