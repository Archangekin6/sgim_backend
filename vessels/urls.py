from rest_framework.routers import DefaultRouter
from .views import VesselViewSet

router = DefaultRouter()
router.register("", VesselViewSet, basename="vessel")
urlpatterns = router.urls