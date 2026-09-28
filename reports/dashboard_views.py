from datetime import datetime, time, timedelta

from django.db.models import Count
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import PasswordResetRequest, User
from alerts.models import Alert
from sar.models import Means

from .models import DailyReport

OPEN_STATUSES = [Alert.Status.NEW, Alert.Status.QUALIFIED, Alert.Status.TRANSMITTED]


def is_operator(user):
    return not user.is_admin_tier


def day_bounds(day):
    start = timezone.make_aware(datetime.combine(day, time.min))
    return start, start + timedelta(days=1)


def scoped_alerts(request):
    """Opérateur : uniquement les alertes de son centre.
    Admin / Super Admin : toutes, ou filtrées avec ?center=<id>."""
    qs = Alert.objects.all()
    if is_operator(request.user):
        return qs.filter(center_id=request.user.center_id)
    center_id = request.query_params.get("center")
    return qs.filter(center_id=center_id) if center_id else qs


def status_breakdown(qs):
    return {row["status"]: row["total"] for row in qs.values("status").annotate(total=Count("id"))}


class AlertsTodayView(APIView):
    """GET /api/dashboard/alerts-today/ : alertes reçues aujourd'hui."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.localdate()
        start, end = day_bounds(today)
        qs = scoped_alerts(request).filter(call_time__gte=start, call_time__lt=end)
        return Response({
            "date": today.isoformat(),
            "count": qs.count(),
            "by_status": status_breakdown(qs),
            "by_category": list(qs.values("category__name").annotate(total=Count("id")).order_by("-total")),
        })


class IncidentsOpenView(APIView):
    """GET /api/dashboard/incidents-open/ : alertes non clôturées
    (incident = alerte depuis la fusion de la v2)."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = scoped_alerts(request).filter(status__in=OPEN_STATUSES)
        return Response({
            "count": qs.count(),
            "high_priority_count": qs.filter(priority__level__gte=3).count(),
            "by_status": status_breakdown(qs),
            "by_category": list(qs.values("category__name").annotate(total=Count("id")).order_by("-total")),
        })


class PersonnelAvailableView(APIView):
    """GET /api/dashboard/personnel-available/ : disponibilité des moyens de secours."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        means = Means.objects.all()
        center_id = request.query_params.get("center")
        if center_id:
            means = means.filter(center_id=center_id)

        by_availability = {
            row["availability"]: row["total"]
            for row in means.values("availability").annotate(total=Count("id"))
        }
        available_by_type = list(
            means.filter(availability=Means.Availability.AVAILABLE)
            .values("means_type__name").annotate(total=Count("id")).order_by("-total")
        )
        return Response({
            "total": means.count(),
            "available": by_availability.get(Means.Availability.AVAILABLE, 0),
            "engaged": by_availability.get(Means.Availability.ENGAGED, 0),
            "unavailable": by_availability.get(Means.Availability.UNAVAILABLE, 0),
            "available_by_type": available_by_type,
        })


class StatsByRoleView(APIView):
    """GET /api/dashboard/stats/by-role/ : contenu adapté au rôle de l'utilisateur connecté."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.localdate()
        start, end = day_bounds(today)
        alerts = scoped_alerts(request)

        data = {
            "role": user.role,
            "scope": "center" if is_operator(user) else "global",
            "alerts_today": alerts.filter(call_time__gte=start, call_time__lt=end).count(),
            "alerts_open": alerts.filter(status__in=OPEN_STATUSES).count(),
            "alerts_by_status": status_breakdown(alerts),
        }

        if is_operator(user):
            data["team"] = user.team
            data["daily_report_submitted_today"] = DailyReport.objects.filter(
                center_id=user.center_id, team=user.team, report_date=today
            ).exists()
        else:
            data["alerts_last_30_days"] = alerts.filter(
                call_time__gte=timezone.now() - timedelta(days=30)
            ).count()
            data["alerts_by_center"] = list(
                alerts.values("center__name").annotate(total=Count("id")).order_by("-total")
            )
            data["daily_reports_pending_validation"] = DailyReport.objects.filter(is_validated=False).count()
            data["means_available"] = Means.objects.filter(availability=Means.Availability.AVAILABLE).count()

            if user.role == User.Role.SUPERADMIN or user.is_superuser:
                data["pending_password_resets"] = PasswordResetRequest.objects.filter(
                    status=PasswordResetRequest.Status.PENDING
                ).count()
                data["active_users"] = User.objects.filter(is_active=True).count()

        return Response(data)