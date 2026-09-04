from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from accounts.models import User
from centers.models import Center
from references.models import AlertSource, IncidentCategory


class AlertWorkflowTests(APITestCase):
    """Vérifie que le cycle de vie complet d'une alerte fonctionne,
    pour détecter automatiquement toute régression future."""

    def setUp(self):
        self.center = Center.objects.create(
            name="MRCC Abidjan", code="MRCC-ABJ", center_type="MRCC", city="Abidjan"
        )
        self.channel = AlertSource.objects.create(name="VHF")
        self.category = IncidentCategory.objects.create(name="Sûreté")
        self.user = User.objects.create_user(
            username="testop", password="TestPass123!",
            role=User.Role.OPERATOR, center=self.center,
        )
        self.client.force_authenticate(user=self.user)

    def test_create_alert_generates_number(self):
        response = self.client.post("/api/alerts/", {
            "call_time": "2026-09-03T22:00:00Z",
            "channel": str(self.channel.id),
            "category": str(self.category.id),
            "description": "Test automatisé",
            "operator_signature": "Testeur",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["number"].startswith("ALT-MRCC-ABJ-"))
        self.assertEqual(response.data["status"], "NEW")

    def test_alert_without_user_center_fails_cleanly(self):
        """Reproduit le cas limite corrigé au point 1 : un opérateur
        sans centre assigné doit recevoir une erreur claire, pas un crash."""
        orphan_user = User.objects.create_user(
            username="orphan", password="TestPass123!", role=User.Role.OPERATOR,
        )
        self.client.force_authenticate(user=orphan_user)
        response = self.client.post("/api/alerts/", {
            "call_time": "2026-09-03T22:00:00Z",
            "channel": str(self.channel.id),
            "category": str(self.category.id),
            "description": "Test sans centre",
            "operator_signature": "Testeur",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_status_creates_history_entry(self):
        create_response = self.client.post("/api/alerts/", {
            "call_time": "2026-09-03T22:00:00Z",
            "channel": str(self.channel.id),
            "category": str(self.category.id),
            "description": "Test statut",
            "operator_signature": "Testeur",
        })
        alert_id = create_response.data["id"]

        response = self.client.post(f"/api/alerts/{alert_id}/change_status/", {
            "status": "QUALIFIED",
            "comment": "Test",
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "QUALIFIED")
        self.assertEqual(len(response.data["history"]), 1)