from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated

from .models import Meeting
from .serializers import MeetingSerializer


class MeetingViewSet(viewsets.ModelViewSet):
    queryset = Meeting.objects.select_related("created_by").all()
    serializer_class = MeetingSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # nécessaire pour recevoir un fichier PDF
    search_fields = ["title", "minutes"]