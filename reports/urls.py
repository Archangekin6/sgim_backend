from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import DailyReportViewSet, DashboardView

router = DefaultRouter()
router.register("daily", DailyReportViewSet, basename="daily-report")

urlpatterns = router.urls + [
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]