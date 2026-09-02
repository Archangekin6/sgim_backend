from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("alert-sources", views.AlertSourceViewSet, basename="alert-source")
router.register("priorities", views.PriorityViewSet, basename="priority")
router.register("severities", views.SeverityViewSet, basename="severity")
router.register("vessel-types", views.VesselTypeViewSet, basename="vessel-type")
router.register("incident-categories", views.IncidentCategoryViewSet, basename="incident-category")
router.register("means-categories", views.MeansCategoryViewSet, basename="means-category")
router.register("means-types", views.MeansTypeViewSet, basename="means-type")
router.register("partner-types", views.PartnerTypeViewSet, basename="partner-type")
router.register("person-roles", views.PersonRoleViewSet, basename="person-role")
router.register("person-statuses", views.PersonStatusViewSet, basename="person-status")

urlpatterns = router.urls