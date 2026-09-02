from django.contrib import admin
from .models import EventLog


@admin.register(EventLog)
class EventLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "action_type", "user", "description")
    list_filter = ("action_type",)
    search_fields = ("description",)
    readonly_fields = [f.name for f in EventLog._meta.fields]

    def has_add_permission(self, request):
        return False