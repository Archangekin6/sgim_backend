from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from .models import EventLog

ACTION_COLORS = {
    "CREATE": "#1E7A4C",
    "UPDATE": "#1B6E8C",
    "STATUS_CHANGE": "#A67C00",
    "TRANSMIT": "#6A4C93",
    "ENGAGEMENT": "#B5651D",
    "LOGIN": "#5A6672",
}


@admin.register(EventLog)
class EventLogAdmin(ModelAdmin):
    list_display = ("timestamp", "colored_action", "user", "description")
    list_filter = ("action_type",)
    search_fields = ("description",)
    date_hierarchy = "timestamp"
    readonly_fields = [f.name for f in EventLog._meta.fields]

    def has_add_permission(self, request):
        return False

    def colored_action(self, obj):
        color = ACTION_COLORS.get(obj.action_type, "#5A6672")
        return format_html(
            '<span style="background:{}22;color:{};padding:3px 10px;border-radius:12px;'
            'font-weight:600;font-size:11px;">{}</span>',
            color, color, obj.get_action_type_display(),
        )
    colored_action.short_description = "Action"