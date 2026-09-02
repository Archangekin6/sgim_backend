from django.core.management.base import BaseCommand
from django.db import transaction

from centers.models import Center
from references import models as ref


class Command(BaseCommand):
    help = "Initialise les référentiels de base et les centres MRCC/MRSC (spec v2)"

    @transaction.atomic
    def handle(self, *args, **options):
        Center.objects.get_or_create(
            code="MRCC-ABJ",
            defaults={"name": "MRCC Abidjan", "center_type": Center.CenterType.MRCC, "city": "Abidjan"},
        )
        Center.objects.get_or_create(
            code="MRSC-SP",
            defaults={"name": "MRSC San Pedro", "center_type": Center.CenterType.MRSC, "city": "San Pedro"},
        )
        self.stdout.write(self.style.SUCCESS("Centres OK"))

        for i, name in enumerate(["VHF", "Téléphone", "Email", "WhatsApp", "Autre"], start=1):
            ref.AlertSource.objects.get_or_create_clean(name, defaults={"order": i})

        for i, (name, level) in enumerate([
            ("Faible", 1), ("Moyenne", 2), ("Élevée", 3), ("Critique", 4),
        ], start=1):
            ref.Priority.objects.get_or_create_clean(name, defaults={"order": i, "level": level})

        for i, (name, level) in enumerate([
            ("Mineure", 1), ("Modérée", 2), ("Grave", 3), ("Critique", 4),
        ], start=1):
            ref.Severity.objects.get_or_create_clean(name, defaults={"order": i, "level": level})

        for i, name in enumerate([
            "Sûreté", "Pollution Maritime", "Urgences Médicales en Mer (TMAS)", "Sécurité Environnementale",
        ], start=1):
            ref.IncidentCategory.objects.get_or_create_clean(name, defaults={"order": i})

        for i, name in enumerate([
            "Pétrolier", "Porte-conteneurs", "Navire de pêche", "Cargo vrac", "Navire militaire",
            "Navire de plaisance", "Petite embarcation", "Navire de sauvetage", "Autre",
        ], start=1):
            ref.VesselType.objects.get_or_create_clean(name, defaults={"order": i})

        cat_mer, _ = ref.MeansCategory.objects.get_or_create_clean("Maritime", defaults={"order": 1})
        cat_air, _ = ref.MeansCategory.objects.get_or_create_clean("Aérien", defaults={"order": 2})
        for i, (name, cat) in enumerate([
            ("Vedette SAR", cat_mer), ("Patrouilleur", cat_mer), ("Navire militaire", cat_mer),
            ("Remorqueur", cat_mer), ("Hélicoptère", cat_air), ("Avion", cat_air), ("Drone", cat_air),
        ], start=1):
            ref.MeansType.objects.get_or_create_clean(name, defaults={"order": i, "category": cat})

        for i, name in enumerate([
            "Marine Nationale", "Police Maritime", "CIAPOL", "Clinique Farah", "Sodexam",
        ], start=1):
            ref.PartnerType.objects.get_or_create_clean(name, defaults={"order": i})

        for i, name in enumerate([
            "Victime", "Rescapé", "Disparu", "Décédé", "Membre d'équipage", "Passager", "Témoin",
        ], start=1):
            ref.PersonRole.objects.get_or_create_clean(name, defaults={"order": i})

        for i, name in enumerate([
            "Indéterminé", "Indemne", "Blessé léger", "Blessé grave", "Décédé", "Disparu", "Sain et sauf",
        ], start=1):
            ref.PersonStatus.objects.get_or_create_clean(name, defaults={"order": i})

        self.stdout.write(self.style.SUCCESS("Référentiels v2 initialisés."))