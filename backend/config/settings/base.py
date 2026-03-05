# config/settings/base.py — FULL REPLACEMENT
# Changes from original:
#   + DATABASE_ROUTERS wired (FIX 7 — read replica)
#   + DATABASES["replica"] added (FIX 7)
#   + Additional throttle rates for custom throttle classes (FIX 4)
#   + APP_VERSION setting

from pathlib import Path
import environ

env = environ.Env()
BASE_DIR = Path(__file__).resolve().parent.parent.parent
environ.Env.read_env(BASE_DIR / ".env")

APP_VERSION = "1.0.0"

SECRET_KEY    = env("SECRET_KEY")
DEBUG         = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]
THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "django_filters",
    "channels",
    "drf_spectacular",
    "django_ratelimit",
    "encrypted_model_fields",
    "django_celery_beat",
]
LOCAL_APPS = [
    "apps.accounts",
    "apps.properties",
    "apps.verification",
    "apps.escrow",
    "apps.messaging",
    "apps.services",
    "apps.agents",
    "apps.audit",
    "apps.notifications",
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS
AUTH_USER_MODEL = "accounts.CustomUser"

# ── Databases ────────────────────────────────────────────────────────────────
# FIX 1: DATABASE_URL should point to PgBouncer in production:
#   DATABASE_URL=postgres://user:pass@pgbouncer:6432/ardhitrust
DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default="postgres://ardhitrust:password@localhost:5432/ardhitrust"
    ),
    # FIX 7: Read replica — set DATABASE_REPLICA_URL in .env
    # In development, replica falls back to primary (same URL)
    "replica": env.db(
        "DATABASE_REPLICA_URL",
        default=env("DATABASE_URL",
                    default="postgres://ardhitrust:password@localhost:5432/ardhitrust")
    ),
}

# FIX 7: Route reads to replica, writes to primary
DATABASE_ROUTERS = ["core.db_router.PrimaryReplicaRouter"]

# ── Redis / Channels / Celery ─────────────────────────────────────────────────
_REDIS = env("REDIS_URL", default="redis://localhost:6379/0")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": _REDIS,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
            "CONNECTION_POOL_KWARGS": {"max_connections": 100},
        },
    }
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG":  {"hosts": [_REDIS]},
    }
}

CELERY_BROKER_URL        = _REDIS
CELERY_RESULT_BACKEND    = _REDIS
CELERY_TASK_SERIALIZER   = "json"
CELERY_ACCEPT_CONTENT    = ["json"]
CELERY_TASK_TIME_LIMIT   = 300
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TIMEZONE          = "Africa/Nairobi"

# ── Middleware ────────────────────────────────────────────────────────────────
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF     = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS":    [],
    "APP_DIRS": True,
    "OPTIONS": {
        "context_processors": [
            "django.template.context_processors.debug",
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        ],
    },
}]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ── DRF ───────────────────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    # FIX 4: Extended throttle rates including custom scopes
    "DEFAULT_THROTTLE_RATES": {
        "anon":            "20/minute",
        "user":            "200/minute",
        "ai_agent":        "10/minute",     # FIX 4: AI endpoints (cost control)
        "verification":    "5/minute",      # Government API quota protection
        "kyc_submit":      "3/hour",        # KYC spam prevention
        "register":        "5/hour",        # Account creation spam prevention
        "mpesa_callback":  "10000/minute",  # Safaricom callback volume
    },
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_SCHEMA_CLASS":   "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER":      "core.exceptions.custom_exception_handler",
    "DEFAULT_PAGINATION_CLASS": "core.pagination.StandardCursorPagination",
    "PAGE_SIZE":               12,
}

# ── i18n / Static ─────────────────────────────────────────────────────────────
LANGUAGE_CODE      = "en-us"
TIME_ZONE          = "Africa/Nairobi"
USE_I18N           = True
USE_TZ             = True
STATIC_URL         = "/static/"
STATIC_ROOT        = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=["http://localhost:5173", "http://localhost:3000"],
)

FIELD_ENCRYPTION_KEYS = env.list(
    "FIELD_ENCRYPTION_KEYS",
    default=["aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"],
)

# ── External APIs ─────────────────────────────────────────────────────────────
ARDHISASA_API_URL         = env("ARDHISASA_API_URL",  default="")
ARDHISASA_API_KEY         = env("ARDHISASA_API_KEY",  default="")
ARDHISASA_MOCK_MODE       = env.bool("ARDHISASA_MOCK_MODE", default=True)
IPRS_API_URL              = env("IPRS_API_URL",       default="")
IPRS_API_KEY              = env("IPRS_API_KEY",       default="")
IPRS_MOCK_MODE            = env.bool("IPRS_MOCK_MODE", default=True)
KRA_API_URL               = env("KRA_API_URL",        default="")
KRA_API_KEY               = env("KRA_API_KEY",        default="")
ANTHROPIC_API_KEY         = env("ANTHROPIC_API_KEY",  default="")
MPESA_ENV                 = env("MPESA_ENV",           default="sandbox")
MPESA_CONSUMER_KEY        = env("MPESA_CONSUMER_KEY",  default="")
MPESA_CONSUMER_SECRET     = env("MPESA_CONSUMER_SECRET", default="")
MPESA_SHORTCODE           = env("MPESA_SHORTCODE",     default="")
MPESA_PASSKEY             = env("MPESA_PASSKEY",       default="")
MPESA_INITIATOR_NAME      = env("MPESA_INITIATOR_NAME", default="")
MPESA_SECURITY_CREDENTIAL = env("MPESA_SECURITY_CREDENTIAL", default="")
BASE_URL                  = env("BASE_URL",            default="http://localhost:8000")

EMAIL_BACKEND       = env("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
EMAIL_HOST          = env("EMAIL_HOST",    default="")
EMAIL_PORT          = env.int("EMAIL_PORT", default=587)
EMAIL_HOST_USER     = env("EMAIL_HOST_USER",     default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS       = True
DEFAULT_FROM_EMAIL  = "ArdhiTrust <noreply@ardhitrust.co.ke>"

AFRICAS_TALKING_USERNAME = env("AFRICAS_TALKING_USERNAME", default="sandbox")
AFRICAS_TALKING_API_KEY  = env("AFRICAS_TALKING_API_KEY",  default="")

SENTRY_DSN = env("SENTRY_DSN", default="")

AWS_ACCESS_KEY_ID       = env("AWS_ACCESS_KEY_ID",       default="")
AWS_SECRET_ACCESS_KEY   = env("AWS_SECRET_ACCESS_KEY",   default="")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME", default="ardhitrust-documents")
AWS_S3_REGION_NAME      = env("AWS_S3_REGION_NAME",      default="af-south-1")