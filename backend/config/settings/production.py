from .base import *   # ← ADD THIS
from datetime import timedelta  # ← ADD THIS


# config/settings/production.py
SECURE_SSL_REDIRECT              = True
SECURE_HSTS_SECONDS              = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS   = True
SECURE_HSTS_PRELOAD              = True
SECURE_CONTENT_TYPE_NOSNIFF      = True
SECURE_BROWSER_XSS_FILTER        = True
X_FRAME_OPTIONS                  = "DENY"
SESSION_COOKIE_SECURE            = True
SESSION_COOKIE_HTTPONLY          = True
SESSION_COOKIE_SAMESITE          = "Strict"
CSRF_COOKIE_SECURE               = True
CSRF_COOKIE_HTTPONLY             = True

# Field encryption — rotate every 6 months, keep old keys for decryption
FIELD_ENCRYPTION_KEYS = env.list("FIELD_ENCRYPTION_KEYS")

# Short JWT lifetime — critical for a financial platform
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME":  timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS":  True,
    "BLACKLIST_AFTER_ROTATION": True,
}