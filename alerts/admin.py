from django.contrib import admin
from .models import Alert, AlertHistory, AlertPerson


class AlertPersonInline(admin.TabularInline):
    model = AlertPerson
    extra = 0


class AlertHistoryInline(admin.TabularInline):
    model = AlertHistory
    extra = 0
    readonly_fields = ("old_status", "new_status", "user", "created_at", "comment")
    can_delete = False


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ("number", "center", "category", "priority", "status", "call_time", "operator_signature")
    list_filter = ("status", "center", "category", "priority")
    search_fields = ("number", "description", "operator_signature")
    readonly_fields = ("number",)
    inlines = [AlertPersonInline, AlertHistoryInline]