from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from drf_spectacular.utils import extend_schema, extend_schema_view
from accounts.permissions import IsAdminTier
from . import models, serializers

_WRITE_NOTE = "⚠️ Réservé aux administrateurs (ADMIN / SUPERADMIN)."
_READ_NOTE = "Accessible à tout utilisateur authentifié. Ajouter `?include_inactive=true` pour inclure les entrées désactivées."
_CHANNEL_NOTE = (
    "**Canal de réception d'une alerte** (ex : VHF, Téléphone, Email, WhatsApp, OVH...).\n\n"
    "Cet endpoint alimente le menu déroulant `channel` du formulaire « Nouvelle Alerte ». "
    "Envoyer l'`id` (UUID) de l'entrée choisie dans le champ `channel` lors de la création.\n\n"
    "Un administrateur peut ajouter un nouveau canal via `POST /api/references/alert-sources/`.\n\n"
    + _READ_NOTE
)


class ReferenceViewSetBase(viewsets.ModelViewSet):
    """
    Lecture (GET) : tout utilisateur authentifié.
    Écriture (POST / PUT / PATCH / DELETE) : administrateurs uniquement.
    """

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsAdminTier()]

    def get_queryset(self):
        qs = self.queryset
        # Les admins peuvent demander include_inactive=true pour voir les entrées désactivées
        if self.request.query_params.get("include_inactive") != "true":
            qs = qs.filter(is_active=True)
        return qs


def _schema(label: str, plural: str, list_note: str = None):
    """Génère les annotations extend_schema_view pour un ViewSet de référence."""
    return extend_schema_view(
        list=extend_schema(
            summary=f"Lister les {plural}",
            description=list_note or _READ_NOTE,
            tags=["Références"],
        ),
        retrieve=extend_schema(
            summary=f"Détail d'un(e) {label}",
            tags=["Références"],
        ),
        create=extend_schema(
            summary=f"Créer un(e) {label}",
            description=f"{_WRITE_NOTE} Le champ `code` est généré automatiquement depuis le `name` (slug).",
            tags=["Références"],
        ),
        update=extend_schema(
            summary=f"Remplacer un(e) {label}",
            description=_WRITE_NOTE,
            tags=["Références"],
        ),
        partial_update=extend_schema(
            summary=f"Modifier partiellement un(e) {label}",
            description=_WRITE_NOTE,
            tags=["Références"],
        ),
        destroy=extend_schema(
            summary=f"Supprimer un(e) {label}",
            description=_WRITE_NOTE,
            tags=["Références"],
        ),
    )


@_schema("source d'alerte", "sources d'alerte", list_note=_CHANNEL_NOTE)
class AlertSourceViewSet(ReferenceViewSetBase):
    queryset = models.AlertSource.objects.all()
    serializer_class = serializers.AlertSourceSerializer


@_schema("priorité", "priorités")
class PriorityViewSet(ReferenceViewSetBase):
    queryset = models.Priority.objects.all()
    serializer_class = serializers.PrioritySerializer


@_schema("sévérité", "sévérités")
class SeverityViewSet(ReferenceViewSetBase):
    queryset = models.Severity.objects.all()
    serializer_class = serializers.SeveritySerializer


@_schema("type de navire", "types de navire")
class VesselTypeViewSet(ReferenceViewSetBase):
    queryset = models.VesselType.objects.all()
    serializer_class = serializers.VesselTypeSerializer


@_schema("catégorie d'incident", "catégories d'incident")
class IncidentCategoryViewSet(ReferenceViewSetBase):
    queryset = models.IncidentCategory.objects.all()
    serializer_class = serializers.IncidentCategorySerializer


@_schema("catégorie de moyen", "catégories de moyen")
class MeansCategoryViewSet(ReferenceViewSetBase):
    queryset = models.MeansCategory.objects.all()
    serializer_class = serializers.MeansCategorySerializer


@_schema("type de moyen", "types de moyen")
class MeansTypeViewSet(ReferenceViewSetBase):
    queryset = models.MeansType.objects.select_related("category").all()
    serializer_class = serializers.MeansTypeSerializer
    filterset_fields = ["category"]


@_schema("type de partenaire", "types de partenaire")
class PartnerTypeViewSet(ReferenceViewSetBase):
    queryset = models.PartnerType.objects.all()
    serializer_class = serializers.PartnerTypeSerializer


@_schema("rôle de personne", "rôles de personne")
class PersonRoleViewSet(ReferenceViewSetBase):
    queryset = models.PersonRole.objects.all()
    serializer_class = serializers.PersonRoleSerializer


@_schema("statut de personne", "statuts de personne")
class PersonStatusViewSet(ReferenceViewSetBase):
    queryset = models.PersonStatus.objects.all()
    serializer_class = serializers.PersonStatusSerializer