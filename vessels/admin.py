from django.contrib import admin
from .models import Vessel


@admin.register(Vessel)
class VesselAdmin(admin.ModelAdmin):
    list_display = ("name", "vessel_type", "flag", "mmsi", "imo")
    list_filter = ("vessel_type", "flag")
    search_fields = ("name", "mmsi", "imo")