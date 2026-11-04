from django.urls import path
from .views import CoordinationView

urlpatterns = [
    path("", CoordinationView.as_view(), name="coordination"),
]
