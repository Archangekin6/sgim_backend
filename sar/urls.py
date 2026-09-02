from rest_framework.routers import DefaultRouter
from .views import MeansEngagementViewSet, MeansViewSet

router = DefaultRouter()
router.register("engagements", MeansEngagementViewSet, basename="means-engagement")
router.register("", MeansViewSet, basename="means")
urlpatterns = router.urls