from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import AlertExcelExportView, AlertPDFView, DailyReportViewSet, DashboardView

router = DefaultRouter()
router.register("daily", DailyReportViewSet, basename="daily-report")

urlpatterns = router.urls + [
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    # Exports
    path("exports/alerts/<uuid:pk>/pdf/", AlertPDFView.as_view(), name="alert-pdf"),
    path("exports/alerts/excel/", AlertExcelExportView.as_view(), name="alerts-excel"),
]