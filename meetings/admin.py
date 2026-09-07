from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from .models import Meeting


@admin.register(Meeting)
class MeetingAdmin(ModelAdmin):
    list_display = ("title", "meeting_date", "created_by", "fiche_link")
    search_fields = ("title", "minutes")
    date_hierarchy = "meeting_date"

    readonly_fields = ("title", "meeting_date", "minutes", "attendance_sheet", "created_by", "created_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def fiche_link(self, obj):
        if obj.attendance_sheet:
            return format_html('<a href="{}" target="_blank">Voir la fiche de présence</a>', obj.attendance_sheet.url)
        return "—"
    fiche_link.short_description = "Fiche de présence"