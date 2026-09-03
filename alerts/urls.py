from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import AlertViewSet, HeatmapView

router = DefaultRouter()
router.register("", AlertViewSet, basename="alert")

urlpatterns = router.urls + [
    path("heatmap/", HeatmapView.as_view(), name="alert-heatmap"),
]