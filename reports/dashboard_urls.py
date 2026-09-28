from django.urls import path

from .dashboard_views import (
    AlertsTodayView,
    IncidentsOpenView,
    PersonnelAvailableView,
    StatsByRoleView,
)

urlpatterns = [
    path("stats/by-role/", StatsByRoleView.as_view(), name="dashboard-stats-by-role"),
    path("alerts-today/", AlertsTodayView.as_view(), name="dashboard-alerts-today"),
    path("incidents-open/", IncidentsOpenView.as_view(), name="dashboard-incidents-open"),
    path("personnel-available/", PersonnelAvailableView.as_view(), name="dashboard-personnel-available"),
]