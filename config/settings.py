from pathlib import Path
from datetime import timedelta
from decouple import config
from django.urls import reverse_lazy

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-remplace-moi-en-prod'
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'unfold',
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'django_filters',
    'corsheaders',
    'drf_spectacular',

    'accounts',
    'centers',
    'references',
    'vessels',
    'partners',
    'alerts',
    'persons',
    'sar',
    'event_logs',
    'reports',
    'meetings',
]

UNFOLD = {
    "SITE_TITLE": "SGIM Admin",
    "SITE_HEADER": "SGIM — MRCC Abidjan",
    "SITE_SUBHEADER": "Système de Gestion des Incidents Maritimes",
    "SITE_SYMBOL": "anchor",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": False,
    "COLORS": {
        "primary": {
            "50": "240 249 255", "100": "224 242 254", "200": "186 230 253",
            "300": "125 211 252", "400": "56 189 248", "500": "14 165 233",
            "600": "2 132 199", "700": "3 105 161", "800": "7 89 133",
            "900": "12 74 110", "950": "8 47 73",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Opérations",
                "separator": True,
                "items": [
                    {"title": "Alertes", "icon": "warning", "link": reverse_lazy("admin:alerts_alert_changelist")},
                    {"title": "Personnes / Victimes", "icon": "groups", "link": reverse_lazy("admin:persons_person_changelist")},
                    {"title": "Moyens de secours", "icon": "directions_boat", "link": reverse_lazy("admin:sar_means_changelist")},
                    {"title": "Rapports journaliers", "icon": "summarize", "link": reverse_lazy("admin:reports_dailyreport_changelist")},
                    {"title": "Réunions", "icon": "groups_2", "link": reverse_lazy("admin:meetings_meeting_changelist")},
                ],
            },
            {
                "title": "Référentiels",
                "separator": True,
                "items": [
                    {"title": "Centres", "icon": "location_city", "link": reverse_lazy("admin:centers_center_changelist")},
                    {"title": "Navires", "icon": "sailing", "link": reverse_lazy("admin:vessels_vessel_changelist")},
                    {"title": "Partenaires", "icon": "handshake", "link": reverse_lazy("admin:partners_partner_changelist")},
                ],
            },
            {
                "title": "Administration",
                "separator": True,
                "items": [
                    {"title": "Utilisateurs", "icon": "manage_accounts", "link": reverse_lazy("admin:accounts_user_changelist")},
                    {"title": "Journal des événements", "icon": "history", "link": reverse_lazy("admin:event_logs_eventlog_changelist")},
                ],
            },
        ],
    },
}

AUTH_USER_MODEL = "accounts.User"

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Base de données SQLite (par défaut)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Abidjan'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    
    'DEFAULT_THROTTLE_RATES': {
        'anon': '20/minute',   # utilisateurs non connectés (ex: tentatives de login)
        'user': '200/minute',  # utilisateurs connectés
    },
}


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
]
CORS_ALLOW_CREDENTIALS = True

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

SPECTACULAR_SETTINGS = {
    'TITLE': 'SGIM API',
    'DESCRIPTION': 'API du Système de Gestion des Incidents Maritimes - MRCC Abidjan / MRSC San Pedro',
    'VERSION': '2.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}