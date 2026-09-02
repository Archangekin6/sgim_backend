from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Center
from .serializers import CenterSerializer


class CenterViewSet(viewsets.ModelViewSet):
    queryset = Center.objects.all()
    serializer_class = CenterSerializer
    permission_classes = [IsAuthenticated]