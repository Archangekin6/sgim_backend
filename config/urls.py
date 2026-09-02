from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('api/users/', include('accounts.urls')),
    path('api/centers/', include('centers.urls')),
    path('api/references/', include('references.urls')),
    path('api/vessels/', include('vessels.urls')),
    path('api/partners/', include('partners.urls')),
    path('api/alerts/', include('alerts.urls')),
    path('api/persons/', include('persons.urls')),
    path('api/sar/', include('sar.urls')),
    path('api/event-logs/', include('event_logs.urls')),
]
