from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from django.conf import settings
from django.conf.urls.static import static

from accounts.views import PasswordResetRequestCreateView

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
    path('api/reports/', include('reports.urls')),
    path('api/meetings/', include('meetings.urls')),
    
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    path('api/auth/password-reset-request/', PasswordResetRequestCreateView.as_view(), name='password-reset-request'),
]

if settings.DEBUG:
     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)