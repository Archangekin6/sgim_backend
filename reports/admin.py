from django.contrib import admin
from .models import DailyReport


@admin.register(DailyReport)
class DailyReportAdmin(admin.ModelAdmin):
    list_display = ("center", "team", "report_date", "is_validated", "email_sent")
    list_filter = ("center", "team", "is_validated")
    search_fields = ("summary",)