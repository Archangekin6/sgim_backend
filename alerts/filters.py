import uuid

import django_filters
from django.db.models import Q

from .models import Alert

ACTIVE_STATUSES = [Alert.Status.NEW, Alert.Status.QUALIFIED, Alert.Status.TRANSMITTED]


def _as_uuid(value):
    try:
        return uuid.UUID(str(value))
    except ValueError:
        return None


class AlertFilter(django_filters.FilterSet):
    """
    status   : NEW, QUALIFIED, TRANSMITTED, CLOSED, ou "active" (= tout sauf CLOSED).
               Plusieurs valeurs possibles, séparées par des virgules.
    priority : UUID, code (ex: elevee) ou nom.
    category : UUID, code (ex: surete) ou nom.
    call_time_after / call_time_before : dates ISO 8601.
    """
    status = django_filters.CharFilter(
        method="filter_status",
        help_text="NEW, QUALIFIED, TRANSMITTED, CLOSED, ou active (tout sauf CLOSED). Valeurs multiples séparées par des virgules.",
    )
    priority = django_filters.CharFilter(
        method="filter_priority",
        help_text="UUID, code (ex : elevee) ou nom de la priorité.",
    )
    category = django_filters.CharFilter(
        method="filter_category",
        help_text="UUID, code (ex : surete) ou nom de la catégorie.",
    )
    call_time_after = django_filters.IsoDateTimeFilter(field_name="call_time", lookup_expr="gte")
    call_time_before = django_filters.IsoDateTimeFilter(field_name="call_time", lookup_expr="lte")

    class Meta:
        model = Alert
        fields = ["center", "channel", "vessel"]

    def filter_status(self, queryset, name, value):
        wanted = []
        for item in value.split(","):
            item = item.strip().upper()
            if item == "ACTIVE":
                wanted.extend(ACTIVE_STATUSES)
            elif item:
                wanted.append(item)
        return queryset.filter(status__in=wanted)

    def _filter_reference(self, queryset, field, value):
        uid = _as_uuid(value)
        if uid:
            return queryset.filter(**{f"{field}_id": uid})
        return queryset.filter(
            Q(**{f"{field}__code__iexact": value}) | Q(**{f"{field}__name__iexact": value})
        )

    def filter_priority(self, queryset, name, value):
        return self._filter_reference(queryset, "priority", value)

    def filter_category(self, queryset, name, value):
        return self._filter_reference(queryset, "category", value)