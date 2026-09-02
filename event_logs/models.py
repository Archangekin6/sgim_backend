import uuid
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class EventLog(models.Model):
    class ActionType(models.TextChoices):
        CREATE = "CREATE", "Création"
        UPDATE = "UPDATE", "Modification"
        STATUS_CHANGE = "STATUS_CHANGE", "Changement de statut"
        TRANSMIT = "TRANSMIT", "Transmission partenaire"
        ENGAGEMENT = "ENGAGEMENT", "Engagement de moyen"
        LOGIN = "LOGIN", "Connexion"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="event_logs"
    )
    action_type = models.CharField(max_length=20, choices=ActionType.choices)
    description = models.TextField(blank=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.CharField(max_length=64, null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        ordering = ["-timestamp"]
        indexes = [models.Index(fields=["action_type"])]

    def __str__(self):
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {self.get_action_type_display()} - {self.user}"