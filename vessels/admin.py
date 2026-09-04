from django.contrib import admin
from .models import Vessel
from unfold.admin import ModelAdmin


@admin.register(Vessel)
class VesselAdmin(ModelAdmin):
    list_display = ("name", "vessel_type", "flag", "mmsi", "imo")
    list_filter = ("vessel_type", "flag")
    search_fields = ("name", "mmsi", "imo")