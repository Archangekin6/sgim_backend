from django.contrib import admin
from .models import Meeting
from unfold.admin import ModelAdmin


@admin.register(Meeting)
class MeetingAdmin(ModelAdmin):
    list_display = ("title", "meeting_date", "created_by")
    search_fields = ("title", "minutes")