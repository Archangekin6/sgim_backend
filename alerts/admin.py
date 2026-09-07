from django.contrib import admin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import path, reverse
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline

from .models import Alert, AlertHistory, AlertPerson

STATUS_COLORS = {
    "NEW": "#B5651D",
    "QUALIFIED": "#A67C00",
    "TRANSMITTED": "#1B6E8C",
    "CLOSED": "#1E7A4C",
}


class AlertPersonInline(TabularInline):
    model = AlertPerson
    extra = 0


class AlertHistoryInline(TabularInline):
    model = AlertHistory
    extra = 0
    readonly_fields = ("old_status", "new_status", "user", "created_at", "comment")
    can_delete = False


@admin.register(Alert)
class AlertAdmin(ModelAdmin):
    list_display = (
        "number", "center", "category", "priority", "colored_status",
        "call_time", "operator_signature", "print_link",
    )
    list_filter = ("status", "center", "category", "priority")
    search_fields = ("number", "description", "operator_signature")
    readonly_fields = ("number",)
    date_hierarchy = "call_time"
    ordering = ("-call_time",)
    inlines = [AlertPersonInline, AlertHistoryInline]
    actions = ["imprimer_selection"]

    def colored_status(self, obj):
        color = STATUS_COLORS.get(obj.status, "#5A6672")
        return format_html(
            '<span style="background:{}22;color:{};padding:3px 10px;border-radius:12px;'
            'font-weight:600;font-size:11px;">{}</span>',
            color, color, obj.get_status_display(),
        )
    colored_status.short_description = "Statut"

    def print_link(self, obj):
        url = reverse("admin:alerts_alert_print", args=[obj.pk])
        return format_html('<a class="button" href="{}" target="_blank">🖨️ Imprimer</a>', url)
    print_link.short_description = "Impression"

    def get_urls(self):
        custom = [
            path("<uuid:pk>/print/", self.admin_site.admin_view(self.print_view), name="alerts_alert_print"),
            path("print-selection/", self.admin_site.admin_view(self.print_selection_view), name="alerts_alert_print_selection"),
        ]
        return custom + super().get_urls()

    def print_view(self, request, pk):
        alert = get_object_or_404(Alert, pk=pk)
        return render(request, "admin/alerts/print_alerts.html", {"alerts": [alert], "title": f"Alerte {alert.number}"})

    def print_selection_view(self, request):
        ids = [i for i in request.GET.get("ids", "").split(",") if i]
        alerts = Alert.objects.filter(pk__in=ids)
        return render(request, "admin/alerts/print_alerts.html", {"alerts": alerts, "title": "Alertes sélectionnées"})

    @admin.action(description="🖨️ Imprimer les alertes sélectionnées")
    def imprimer_selection(self, request, queryset):
        ids = ",".join(str(a.pk) for a in queryset)
        return redirect(reverse("admin:alerts_alert_print_selection") + f"?ids={ids}")