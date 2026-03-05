# config/settings/test.py
#
# BUG FIXED IN THIS VERSION:
#   base.py sets DATABASE_ROUTERS = ["core.db_router.PrimaryReplicaRouter"]
#   which routes all SELECT queries to DATABASES["replica"].
#   The test settings previously only defined DATABASES["default"].
#   Any test that triggered a SELECT (i.e. almost every test) would raise:
#     django.db.utils.ConnectionDoesNotExist: The connection 'replica'
#     doesn't exist.
#
#   Two valid fixes:
#     Option A: Define DATABASES["replica"] pointing to the same test DB.
#     Option B: Override DATABASE_ROUTERS = [] to disable routing in tests.
#
#   We use Option A — it keeps the router active in tests, which means
#   the routing logic itself is also tested. The replica alias just
#   points to the same test database as "default". This is safe because
#   test transactions are rolled back after each test anyway.

from .base import *  # noqa: F401, F403

# ── Test Database ─────────────────────────────────────────────────────────────
# Both "default" and "replica" point to the same test DB.
# The router stays active, exercising routing logic in tests.
# In CI (GitHub Actions), these match the postgres service credentials.
_TEST_DB = {
    "ENGINE":   "django.db.backends.postgresql",
    "NAME":     "ardhitrust_test",
    "USER":     "ardhitrust",
    "PASSWORD": "testpass",
    "HOST":     "localhost",
    "PORT":     "5432",
    # Disable test DB creation for the replica alias —
    # it shares the same physical DB as "default"
    "TEST": {
        "NAME": "ardhitrust_test",
    },
}

DATABASES = {
    "default": _TEST_DB,
    # FIX: replica must be defined or PrimaryReplicaRouter raises
    # ConnectionDoesNotExist on every SELECT query in tests
    "replica": _TEST_DB,
}

# ── Test Speed Optimisations ──────────────────────────────────────────────────
# Run Celery tasks synchronously — no broker needed in tests
CELERY_TASK_ALWAYS_EAGER    = True
CELERY_TASK_EAGER_PROPAGATES = True  # Surface exceptions instead of swallowing

# Fast password hashing — bcrypt is intentionally slow, MD5 is fine for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Mock all external APIs — never call real government systems in tests
ARDHISASA_MOCK_MODE = True
IPRS_MOCK_MODE      = True

# In-memory channel layer — no Redis required for WebSocket tests
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}

# Use console email backend — no SES calls in tests
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Disable Sentry in tests
SENTRY_DSN = ""