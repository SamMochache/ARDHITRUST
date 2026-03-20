# apps/messaging/ws_rate_limiter.py
# FIX: get_redis_connection import moved to module level.
#
# PROBLEM:
#   get_redis_connection was imported inside _get_redis() on every call:
#
#       def _get_redis(self):
#           if self._redis is None:
#               from django_redis import get_redis_connection   ← inside method
#               self._redis = get_redis_connection("default")
#
#   The test patches "apps.messaging.ws_rate_limiter.get_redis_connection"
#   which only works if get_redis_connection is a name in the module's
#   namespace at patch time. A local import inside a method creates a local
#   name, not a module-level name — so the patch target doesn't exist in the
#   module namespace and the mock never intercepts the call. Tests that
#   simulate Redis-down behaviour (fails_open_when_redis_down) would silently
#   call the real Redis instead of raising the mocked exception.
#
# FIX:
#   Import get_redis_connection at module level so it's always present in
#   the module namespace and the test patch target resolves correctly.
#   The lazy connection initialisation in _get_redis() is preserved —
#   we still only create the Redis connection on first use, not at import time.

import time
import logging
from django_redis import get_redis_connection   # FIX: module-level import

logger = logging.getLogger(__name__)

# ── Configuration ──────────────────────────────────────────────────────────────

RATE_LIMIT_MAX_MESSAGES   = 20
RATE_LIMIT_WINDOW_SECONDS = 60
MAX_CONNECTIONS_PER_USER  = 5

_KEY_RATE = "ws:rate:{user_id}"
_KEY_CONN = "ws:conn:{user_id}"


class WebSocketRateLimiter:
    """
    Redis-backed sliding window rate limiter and connection tracker.

    Usage:
        limiter = WebSocketRateLimiter()

        # On connect
        if not limiter.allow_connection(user_id):
            await self.close(code=4029)
        limiter.register_connection(user_id)

        # On each message
        if not limiter.allow_message(user_id):
            await self.send_error("Rate limit exceeded")
            return

        # On disconnect
        limiter.release_connection(user_id)
    """

    def __init__(self):
        self._redis = None

    def _get_redis(self):
        """
        Lazy Redis connection — connection is created on first use, not at
        import time. This avoids issues during Django startup before the
        cache layer is fully configured.

        get_redis_connection is now a module-level name so test patches of
        'apps.messaging.ws_rate_limiter.get_redis_connection' resolve correctly.
        """
        if self._redis is None:
            self._redis = get_redis_connection("default")
        return self._redis

    # ── Message rate limiting ──────────────────────────────────────────────────

    def allow_message(self, user_id: str) -> bool:
        try:
            redis  = self._get_redis()
            key    = _KEY_RATE.format(user_id=user_id)
            now    = time.time()
            window = now - RATE_LIMIT_WINDOW_SECONDS

            pipe = redis.pipeline()
            pipe.zremrangebyscore(key, "-inf", window)
            pipe.zcard(key)
            pipe.zadd(key, {str(now): now})
            pipe.expire(key, RATE_LIMIT_WINDOW_SECONDS + 10)
            results = pipe.execute()

            message_count = results[1]
            return message_count < RATE_LIMIT_MAX_MESSAGES

        except Exception as e:
            logger.warning(f"WebSocket rate limiter Redis error: {e}")
            return True  # fail open

    def get_message_count(self, user_id: str) -> int:
        try:
            redis  = self._get_redis()
            key    = _KEY_RATE.format(user_id=user_id)
            now    = time.time()
            window = now - RATE_LIMIT_WINDOW_SECONDS
            redis.zremrangebyscore(key, "-inf", window)
            return redis.zcard(key)
        except Exception:
            return 0

    # ── Connection tracking ────────────────────────────────────────────────────

    def allow_connection(self, user_id: str) -> bool:
        try:
            redis   = self._get_redis()
            key     = _KEY_CONN.format(user_id=user_id)
            count   = redis.get(key)
            current = int(count) if count else 0
            return current < MAX_CONNECTIONS_PER_USER
        except Exception as e:
            logger.warning(f"WebSocket connection tracker Redis error: {e}")
            return True  # fail open

    def register_connection(self, user_id: str) -> None:
        try:
            redis = self._get_redis()
            key   = _KEY_CONN.format(user_id=user_id)
            pipe  = redis.pipeline()
            pipe.incr(key)
            pipe.expire(key, 86400)
            pipe.execute()
        except Exception as e:
            logger.warning(f"WebSocket register_connection error: {e}")

    def release_connection(self, user_id: str) -> None:
        try:
            redis   = self._get_redis()
            key     = _KEY_CONN.format(user_id=user_id)
            current = redis.get(key)
            if current and int(current) > 0:
                redis.decr(key)
        except Exception as e:
            logger.warning(f"WebSocket release_connection error: {e}")

    def get_connection_count(self, user_id: str) -> int:
        try:
            redis = self._get_redis()
            key   = _KEY_CONN.format(user_id=user_id)
            count = redis.get(key)
            return int(count) if count else 0
        except Exception:
            return 0
