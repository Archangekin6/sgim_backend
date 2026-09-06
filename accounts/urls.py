from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import PasswordResetRequestViewSet, UserViewSet

router = DefaultRouter()
router.register("password-reset-requests", PasswordResetRequestViewSet, basename="password-reset-request")
router.register("", UserViewSet, basename="user")

urlpatterns = router.urls