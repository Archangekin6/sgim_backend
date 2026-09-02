import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from centers.models import Center


class User(AbstractUser):
    class Role(models.TextChoices):
        SUPERADMIN = "SUPERADMIN", "Super Administrateur"
        ADMIN = "ADMIN", "Administrateur"
        OPERATOR = "OPERATOR", "Opérateur"

    class Team(models.TextChoices):
        CAR1 = "CAR1", "Car 1 (Abidjan)"
        CAR2 = "CAR2", "Car 2 (Abidjan)"
        CAR3 = "CAR3", "Car 3 (Abidjan)"
        CAR4 = "CAR4", "Car 4 (Abidjan)"
        MRSC = "MRSC", "MRSC San Pedro"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.OPERATOR)
    team = models.CharField(max_length=20, choices=Team.choices, null=True, blank=True)
    center = models.ForeignKey(Center, on_delete=models.SET_NULL, null=True, blank=True, related_name="users")
    phone = models.CharField(max_length=30, blank=True)

    def __str__(self):
        team_part = f" - {self.get_team_display()}" if self.team else ""
        return f"{self.get_full_name() or self.username} ({self.get_role_display()}{team_part})"

    @property
    def is_admin_tier(self):
        return self.role in (self.Role.ADMIN, self.Role.SUPERADMIN) or self.is_superuser

    def save(self, *args, **kwargs):
        if self.role == self.Role.SUPERADMIN:
            self.is_superuser = True
            self.is_staff = True
        elif self.role == self.Role.ADMIN:
            self.is_staff = True
        super().save(*args, **kwargs)