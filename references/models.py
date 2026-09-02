import re
import uuid
from django.db import models
from django.utils.text import slugify


def clean_label(value: str) -> str:
    """Corrige le bug des listes déroulantes : supprime les espaces en trop."""
    if value is None:
        return ""
    return re.sub(r"\s+", " ", value).strip()


class ReferenceManager(models.Manager):
    def get_or_create_clean(self, name, defaults=None):
        return self.get_or_create(name=clean_label(name), defaults=defaults or {})


class ReferenceBase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.SlugField(max_length=80, unique=True, blank=True)
    name = models.CharField(max_length=150, unique=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    objects = ReferenceManager()

    class Meta:
        abstract = True
        ordering = ["order", "name"]

    def save(self, *args, **kwargs):
        self.name = clean_label(self.name)
        if not self.code:
            self.code = slugify(self.name)[:80]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class AlertSource(ReferenceBase):
    """VHF, Téléphone, Email, WhatsApp, Autre"""


class Priority(ReferenceBase):
    level = models.PositiveSmallIntegerField(default=1)

    class Meta(ReferenceBase.Meta):
        ordering = ["-level", "name"]


class Severity(ReferenceBase):
    level = models.PositiveSmallIntegerField(default=1)

    class Meta(ReferenceBase.Meta):
        ordering = ["-level", "name"]


class VesselType(ReferenceBase):
    """Pétrolier, Porte-conteneurs, Navire de pêche..."""


class IncidentCategory(ReferenceBase):
    """Sûreté, Pollution Maritime, Urgences Médicales (TMAS), Sécurité Environnementale"""


class MeansCategory(ReferenceBase):
    """Maritime, Aérien"""


class MeansType(ReferenceBase):
    category = models.ForeignKey(
        MeansCategory, on_delete=models.PROTECT, null=True, blank=True, related_name="means_types"
    )


class PartnerType(ReferenceBase):
    """Marine Nationale, Police Maritime, CIAPOL, Clinique Farah, Sodexam"""


class PersonRole(ReferenceBase):
    """Victime, Rescapé, Disparu, Décédé, Membre d'équipage, Témoin"""


class PersonStatus(ReferenceBase):
    """Indemne, Blessé léger, Blessé grave, Décédé, Disparu"""