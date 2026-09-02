from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import User
from .permissions import IsSuperAdmin
from .serializers import MeSerializer, UserSerializer


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