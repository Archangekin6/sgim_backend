from rest_framework import viewsets
from accounts.permissions import IsAdminTier
from .models import Partner
from .serializers import PartnerSerializer


class PartnerViewSet(viewsets.ModelViewSet):
    """Réservé aux Admin/Super Admin - retiré de l'interface opérateur (§5 spec v2)."""
    queryset = Partner.objects.select_related("partner_type").all()
    serializer_class = PartnerSerializer
    permission_classes = [IsAdminTier]
    filterset_fields = ["partner_type", "is_active"]
    search_fields = ["name", "email", "phone"]