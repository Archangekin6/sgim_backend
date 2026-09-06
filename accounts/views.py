from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import User
from .permissions import IsSuperAdmin
from .serializers import MeSerializer, UserSerializer

from django.utils import timezone
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from .models import PasswordResetRequest
from .serializers import (
    BulkResolveSerializer,
    PasswordResetRequestCreateSerializer,
    PasswordResetRequestSerializer,
    ResolvePasswordResetSerializer,
)



class UserViewSet(viewsets.ModelViewSet):
    """Gestion des comptes - réservée au Super Administrateur."""
    queryset = User.objects.select_related("center").all()
    serializer_class = UserSerializer
    permission_classes = [IsSuperAdmin]
    filterset_fields = ["role", "team", "center", "is_active"]
    search_fields = ["username", "first_name", "last_name", "email"]

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        return Response(MeSerializer(request.user).data)
    

class PasswordResetRequestCreateView(APIView):
    """
    Endpoint PUBLIC : un utilisateur qui a oublié son mot de passe signale
    sa demande avec juste son identifiant. Aucune authentification requise
    (il ne peut, par définition, pas se connecter).
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(username=serializer.validated_data["username"])
        PasswordResetRequest.objects.create(user=user, note=serializer.validated_data.get("note", ""))
        return Response(
            {"detail": "Demande enregistrée. Un administrateur va réinitialiser votre mot de passe."},
            status=status.HTTP_201_CREATED,
        )


class PasswordResetRequestViewSet(viewsets.ReadOnlyModelViewSet):
    """Liste des demandes de réinitialisation - réservé au Super Administrateur."""
    queryset = PasswordResetRequest.objects.select_related("user", "resolved_by").all()
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [IsSuperAdmin]
    filterset_fields = ["status", "user"]

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        """Traite UNE demande."""
        reset_request = self.get_object()
        serializer = ResolvePasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reset_request.user.set_password(serializer.validated_data["new_password"])
        reset_request.user.save()

        reset_request.status = PasswordResetRequest.Status.RESOLVED
        reset_request.resolved_by = request.user
        reset_request.resolved_at = timezone.now()
        reset_request.save()

        return Response(PasswordResetRequestSerializer(reset_request).data)

    @action(detail=False, methods=["post"])
    def bulk_resolve(self, request):
        """Traite PLUSIEURS demandes en un seul appel (le cumul demandé)."""
        serializer = BulkResolveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        results = []
        for item in serializer.validated_data["items"]:
            try:
                reset_request = PasswordResetRequest.objects.get(pk=item["id"])
            except PasswordResetRequest.DoesNotExist:
                results.append({"id": str(item["id"]), "error": "Demande introuvable"})
                continue

            reset_request.user.set_password(item["new_password"])
            reset_request.user.save()
            reset_request.status = PasswordResetRequest.Status.RESOLVED
            reset_request.resolved_by = request.user
            reset_request.resolved_at = timezone.now()
            reset_request.save()
            results.append({"id": str(item["id"]), "username": reset_request.user.username, "status": "resolved"})

        return Response({"results": results})