from pathlib import Path
import environ

# ── Bootstrap ──────────────────────────────────────────────────────────────
env = environ.Env()
BASE_DIR = Path(__file__).resolve().parent.parent.parent
environ.Env.read_env(BASE_DIR / ".env")   # MUST be before any env() calls

# ── Core ────────────────────────────────────────────────────────────────────
SECRET_KEY    = env("SECRET_KEY")
DEBUG         = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

# ── Apps ────────────────────────────────────────────────────────────────────
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

# ── Database ────────────────────────────────────────────────────────────────
DATABASES = {
    "default": env.db("DATABASE_URL", default="postgres://ardhitrust:password@localhost:5432/ardhitrust")
}

# ── Cache / Channels / Celery ───────────────────────────────────────────────
_REDIS = env("REDIS_URL", default="redis://localhost:6379/0")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": _REDIS,
    }
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [_REDIS]},
    }
}

CELERY_BROKER_URL          = _REDIS
CELERY_RESULT_BACKEND      = _REDIS
CELERY_TASK_SERIALIZER     = "json"
CELERY_ACCEPT_CONTENT      = ["json"]
CELERY_TASK_TIME_LIMIT     = 300
CELERY_TASK_ALWAYS_EAGER   = False

# ── Middleware ───────────────────────────────────────────────────────────────
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

ROOT_URLCONF       = "config.urls"
WSGI_APPLICATION   = "config.wsgi.application"
ASGI_APPLICATION   = "config.asgi.application"

# ── Templates ────────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ── Auth ─────────────────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ── DRF ──────────────────────────────────────────────────────────────────────
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
    "DEFAULT_THROTTLE_RATES": {
        "anon": "20/minute",
        "user": "200/minute",
        "verification": "5/minute",
        "ai_agent": "10/minute",
    },
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "core.exceptions.custom_exception_handler",
}

# ── i18n / Static ─────────────────────────────────────────────────────────────
LANGUAGE_CODE      = "en-us"
TIME_ZONE          = "Africa/Nairobi"
USE_I18N           = True
USE_TZ             = True
STATIC_URL         = "/static/"
STATIC_ROOT        = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── CORS ──────────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=["http://localhost:5173", "http://localhost:3000"],
)

# ── PII Encryption ────────────────────────────────────────────────────────────
# Production: set FIELD_ENCRYPTION_KEYS in .env as 64-char hex string (32 bytes)
# Generate: python -c "import secrets; print(secrets.token_hex(32))"
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

# ── Email ─────────────────────────────────────────────────────────────────────
EMAIL_BACKEND       = env("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
EMAIL_HOST          = env("EMAIL_HOST",    default="")
EMAIL_PORT          = env.int("EMAIL_PORT", default=587)
EMAIL_HOST_USER     = env("EMAIL_HOST_USER",     default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS       = True
DEFAULT_FROM_EMAIL  = "ArdhiTrust <noreply@ardhitrust.co.ke>"

# ── Africa's Talking SMS ──────────────────────────────────────────────────────
AFRICAS_TALKING_USERNAME = env("AFRICAS_TALKING_USERNAME", default="sandbox")
AFRICAS_TALKING_API_KEY  = env("AFRICAS_TALKING_API_KEY",  default="")

# ── Monitoring ────────────────────────────────────────────────────────────────
SENTRY_DSN = env("SENTRY_DSN", default="")