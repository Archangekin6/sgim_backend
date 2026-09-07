from django.contrib import admin, messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from .models import DailyReport


@admin.register(DailyReport)
class DailyReportAdmin(ModelAdmin):
    list_display = ("center", "team", "report_date", "badge_statut", "email_sent", "action_valider")
    list_filter = ("center", "team", "is_validated")
    search_fields = ("summary",)
    date_hierarchy = "report_date"

    readonly_fields = (
        "center", "report_date", "team", "summary", "alerts_count", "rescues_count",
        "coordinations_count", "calls_received_count", "created_by", "created_at",
        "is_validated", "validated_by", "validated_at", "email_sent",
    )

    def has_add_permission(self, request):
        return False  # créé uniquement par l'agent via l'API

    def has_change_permission(self, request, obj=None):
        return False  # lecture seule : Django affiche alors une fiche de consultation, pas un formulaire

    def badge_statut(self, obj):
        color = "#1E7A4C" if obj.is_validated else "#B5651D"
        label = "Validé" if obj.is_validated else "En attente"
        return format_html('<span style="color:{};font-weight:600;">{}</span>', color, label)
    badge_statut.short_description = "Statut"

    def action_valider(self, obj):
        if obj.is_validated:
            return "—"
        url = reverse("admin:reports_dailyreport_validate", args=[obj.pk])
        return format_html('<a class="button" href="{}">Valider</a>', url)
    action_valider.short_description = "Action"

    def get_urls(self):
        custom = [
            path("<uuid:pk>/validate/", self.admin_site.admin_view(self.validate_view), name="reports_dailyreport_validate"),
        ]
        return custom + super().get_urls()

    def validate_view(self, request, pk):
        report = get_object_or_404(DailyReport, pk=pk)
        if not report.is_validated:
            report.is_validated = True
            report.validated_by = request.user
            report.validated_at = timezone.now()
            report.save()
            messages.success(request, f"Rapport du {report.report_date} validé.")
        return redirect("admin:reports_dailyreport_changelist")