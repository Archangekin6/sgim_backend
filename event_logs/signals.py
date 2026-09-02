from django.db.models.signals import post_save
from django.dispatch import receiver

from alerts.models import Alert, AlertHistory
from sar.models import MeansEngagement

from .models import EventLog


@receiver(post_save, sender=Alert)
def log_alert(sender, instance, created, **kwargs):
    EventLog.objects.create(
        user=instance.created_by,
        action_type=EventLog.ActionType.CREATE if created else EventLog.ActionType.UPDATE,
        description=f"Alerte {instance.number} - {instance.get_status_display()}",
        object_id=str(instance.pk),
    )


@receiver(post_save, sender=AlertHistory)
def log_alert_status_change(sender, instance, created, **kwargs):
    if created:
        EventLog.objects.create(
            user=instance.user,
            action_type=EventLog.ActionType.STATUS_CHANGE,
            description=f"{instance.alert.number}: {instance.old_status} -> {instance.new_status}",
            object_id=str(instance.pk),
        )


@receiver(post_save, sender=MeansEngagement)
def log_means_engagement(sender, instance, created, **kwargs):
    if created:
        EventLog.objects.create(
            user=instance.engaged_by,
            action_type=EventLog.ActionType.ENGAGEMENT,
            description=f"{instance.means} engagé sur {instance.alert.number}",
            object_id=str(instance.pk),
        )