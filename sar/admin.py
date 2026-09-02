from django.contrib import admin
from .models import Means, MeansEngagement


@admin.register(Means)
class MeansAdmin(admin.ModelAdmin):
    list_display = ("name", "means_type", "center", "partner", "availability")
    list_filter = ("availability", "means_type", "center")
    search_fields = ("name", "registration")


@admin.register(MeansEngagement)
class MeansEngagementAdmin(admin.ModelAdmin):
    list_display = ("means", "alert", "engaged_at", "released_at")
    search_fields = ("alert__number", "means__name")