from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Person
from .serializers import PersonSerializer


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.select_related("alert", "vessel", "role", "status").all()
    serializer_class = PersonSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["alert", "role", "status"]
    search_fields = ["name", "nationality"]