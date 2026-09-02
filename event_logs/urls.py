from rest_framework.routers import DefaultRouter
from .views import EventLogViewSet

router = DefaultRouter()
router.register("", EventLogViewSet, basename="event-log")
urlpatterns = router.urls