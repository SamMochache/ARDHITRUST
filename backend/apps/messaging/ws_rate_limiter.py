# apps/messaging/ws_rate_limiter.py
# ─────────────────────────────────────────────────────────────────────────────
# Redis-backed sliding window rate limiter for WebSocket connections.
#
# WHY A SLIDING WINDOW (not a fixed window):
#   Fixed window: user sends 20 messages at 00:59, then 20 more at 01:01.
#   Both windows are within limit but the user sent 40 messages in 2 seconds.
#   Sliding window counts messages in the last N seconds from *now*, so
#   burst attacks across window boundaries are caught correctly.
#
# HOW IT WORKS:
#   Each message adds a Redis ZADD entry with score = current timestamp.
#   ZREMRANGEBYSCORE removes entries older than the window.
#   ZCARD counts remaining entries = messages in the last WINDOW_SECONDS.
#   The key expires automatically (TTL = WINDOW_SECONDS + 10s buffer).
#
# CONNECTION TRACKING:
#   A separate Redis counter tracks open connections per user.
#   Incremented on connect, decremented on disconnect.
#   If the counter exceeds MAX_CONNECTIONS_PER_USER the connection is rejected.
#
# KEYS:
#   ws:rate:{user_id}   → sorted set of message timestamps
#   ws:conn:{user_id}   → integer connection count
# ─────────────────────────────────────────────────────────────────────────────

import time
import logging

logger = logging.getLogger(__name__)

# ── Configuration ─────────────────────────────────────────────────────────────

# Max messages per user within the sliding window
RATE_LIMIT_MAX_MESSAGES = 20

# Sliding window duration in seconds
RATE_LIMIT_WINDOW_SECONDS = 60

# Max concurrent WebSocket connections per user
MAX_CONNECTIONS_PER_USER = 5

# Redis key prefixes
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
        """Lazy Redis connection — avoids import at module load time."""
        if self._redis is None:
            from django_redis import get_redis_connection
            self._redis = get_redis_connection("default")
        return self._redis

    # ── Message rate limiting ─────────────────────────────────────────────────

    def allow_message(self, user_id: str) -> bool:
        """
        Returns True if the user is within the rate limit.
        Uses a sliding window counter in Redis.
        """
        try:
            redis   = self._get_redis()
            key     = _KEY_RATE.format(user_id=user_id)
            now     = time.time()
            window  = now - RATE_LIMIT_WINDOW_SECONDS

            pipe = redis.pipeline()
            # Remove entries older than the window
            pipe.zremrangebyscore(key, "-inf", window)
            # Count remaining entries (messages in the last WINDOW_SECONDS)
            pipe.zcard(key)
            # Add this message attempt with current timestamp as score
            pipe.zadd(key, {str(now): now})
            # Set expiry so the key cleans itself up
            pipe.expire(key, RATE_LIMIT_WINDOW_SECONDS + 10)
            results = pipe.execute()

            message_count = results[1]  # zcard result
            return message_count < RATE_LIMIT_MAX_MESSAGES

        except Exception as e:
            # If Redis is down, fail open — don't block messages
            logger.warning(f"WebSocket rate limiter Redis error: {e}")
            return True

    def get_message_count(self, user_id: str) -> int:
        """Returns current message count in the window. Used in tests."""
        try:
            redis  = self._get_redis()
            key    = _KEY_RATE.format(user_id=user_id)
            now    = time.time()
            window = now - RATE_LIMIT_WINDOW_SECONDS
            redis.zremrangebyscore(key, "-inf", window)
            return redis.zcard(key)
        except Exception:
            return 0

    # ── Connection tracking ───────────────────────────────────────────────────

    def allow_connection(self, user_id: str) -> bool:
        """
        Returns True if the user has fewer than MAX_CONNECTIONS_PER_USER
        active WebSocket connections.
        """
        try:
            redis = self._get_redis()
            key   = _KEY_CONN.format(user_id=user_id)
            count = redis.get(key)
            current = int(count) if count else 0
            return current < MAX_CONNECTIONS_PER_USER
        except Exception as e:
            logger.warning(f"WebSocket connection tracker Redis error: {e}")
            return True  # fail open

    def register_connection(self, user_id: str) -> None:
        """Increment connection counter for a user."""
        try:
            redis = self._get_redis()
            key   = _KEY_CONN.format(user_id=user_id)
            pipe  = redis.pipeline()
            pipe.incr(key)
            # TTL is a safety net — if disconnect is never called, key expires
            pipe.expire(key, 86400)  # 24 hours
            pipe.execute()
        except Exception as e:
            logger.warning(f"WebSocket register_connection error: {e}")

    def release_connection(self, user_id: str) -> None:
        """Decrement connection counter for a user. Never goes below 0."""
        try:
            redis   = self._get_redis()
            key     = _KEY_CONN.format(user_id=user_id)
            current = redis.get(key)
            if current and int(current) > 0:
                redis.decr(key)
        except Exception as e:
            logger.warning(f"WebSocket release_connection error: {e}")

    def get_connection_count(self, user_id: str) -> int:
        """Returns current connection count for a user. Used in tests."""
        try:
            redis = self._get_redis()
            key   = _KEY_CONN.format(user_id=user_id)
            count = redis.get(key)
            return int(count) if count else 0
        except Exception:
            return 0
