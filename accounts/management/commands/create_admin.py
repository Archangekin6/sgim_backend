import os
from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = "Crée (ou met à jour) le compte Super Administrateur à partir des variables d'environnement."

    def handle(self, *args, **options):
        username = os.environ.get("ADMIN_USERNAME")
        email = os.environ.get("ADMIN_EMAIL", "")
        password = os.environ.get("ADMIN_PASSWORD")

        if not username or not password:
            self.stdout.write(self.style.WARNING(
                "ADMIN_USERNAME ou ADMIN_PASSWORD absent(s) des variables d'environnement — commande ignorée."
            ))
            return

        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": email, "role": User.Role.SUPERADMIN},
        )
        user.email = email
        user.role = User.Role.SUPERADMIN
        user.is_superuser = True
        user.is_staff = True
        user.set_password(password)
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f"Super Administrateur '{username}' créé."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Super Administrateur '{username}' mis à jour."))