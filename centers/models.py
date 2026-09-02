from django.db import models


class Center(models.Model):
    class CenterType(models.TextChoices):
        MRCC = "MRCC", "MRCC"
        MRSC = "MRSC", "MRSC"

    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=20, unique=True)
    center_type = models.CharField(max_length=10, choices=CenterType.choices)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default="Côte d'Ivoire")
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.name}"