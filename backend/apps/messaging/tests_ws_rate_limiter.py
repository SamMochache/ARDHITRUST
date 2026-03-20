# apps/messaging/tests_ws_rate_limiter.py
#
# Tests for WebSocketRateLimiter — fully isolated from the consumer.
# Uses Django's cache/Redis backend configured in test settings.

import pytest
import time
from unittest.mock import patch, MagicMock
from apps.messaging.ws_rate_limiter import (
    WebSocketRateLimiter,
    RATE_LIMIT_MAX_MESSAGES,
    RATE_LIMIT_WINDOW_SECONDS,
    MAX_CONNECTIONS_PER_USER,
)


@pytest.fixture
def limiter():
    return WebSocketRateLimiter()


@pytest.fixture
def mock_redis(limiter):
    """
    Inject a mock Redis client so tests don't need a real Redis instance.
    The mock uses a simple in-memory dict to simulate sorted sets and counters.
    """
    store: dict = {}

    class FakePipeline:
        def __init__(self):
            self._cmds = []

        def zremrangebyscore(self, key, mn, mx):
            self._cmds.append(("zremrangebyscore", key, mn, mx))
            return self

        def zcard(self, key):
            self._cmds.append(("zcard", key))
            return self

        def zadd(self, key, mapping):
            self._cmds.append(("zadd", key, mapping))
            return self

        def expire(self, key, ttl):
            self._cmds.append(("expire", key, ttl))
            return self

        def incr(self, key):
            self._cmds.append(("incr", key))
            return self

        def execute(self):
            results = []
            for cmd in self._cmds:
                if cmd[0] == "zremrangebyscore":
                    key = cmd[1]
                    store.setdefault(key, {})
                    results.append(None)
                elif cmd[0] == "zcard":
                    key = cmd[1]
                    results.append(len(store.get(key, {})))
                elif cmd[0] == "zadd":
                    key = cmd[1]
                    store.setdefault(key, {}).update(cmd[2])
                    results.append(1)
                elif cmd[0] == "expire":
                    results.append(True)
                elif cmd[0] == "incr":
                    key = cmd[1]
                    store[key] = store.get(key, b"0")
                    val = int(store[key]) + 1
                    store[key] = str(val).encode()
                    results.append(val)
            return results

    class FakeRedis:
        def pipeline(self):
            return FakePipeline()

        def get(self, key):
            return store.get(key)

        def incr(self, key):
            val = int(store.get(key, b"0")) + 1
            store[key] = str(val).encode()
            return val

        def decr(self, key):
            val = max(0, int(store.get(key, b"1")) - 1)
            store[key] = str(val).encode()
            return val

        def expire(self, key, ttl):
            return True

        def zremrangebyscore(self, key, mn, mx):
            store.setdefault(key, {})

        def zcard(self, key):
            return len(store.get(key, {}))

    fake = FakeRedis()
    limiter._redis = fake
    return fake, store


# ── Message rate limiting ─────────────────────────────────────────────────────

class TestMessageRateLimit:

    def test_first_message_allowed(self, limiter, mock_redis):
        assert limiter.allow_message("user-1") is True

    def test_messages_within_limit_allowed(self, limiter, mock_redis):
        for _ in range(RATE_LIMIT_MAX_MESSAGES - 1):
            assert limiter.allow_message("user-2") is True

    def test_message_at_limit_blocked(self, limiter, mock_redis):
        # Send exactly MAX messages
        for _ in range(RATE_LIMIT_MAX_MESSAGES):
            limiter.allow_message("user-3")
        # Next message should be blocked
        assert limiter.allow_message("user-3") is False

    def test_different_users_independent_limits(self, limiter, mock_redis):
        # Exhaust user-4's limit
        for _ in range(RATE_LIMIT_MAX_MESSAGES):
            limiter.allow_message("user-4")
        # user-5 should still be allowed
        assert limiter.allow_message("user-5") is True

    def test_fails_open_when_redis_down(self, limiter):
        """If Redis is unavailable, messages should be allowed (fail open)."""
        limiter._redis = None
        with patch("apps.messaging.ws_rate_limiter.get_redis_connection",
                   side_effect=Exception("Redis down")):
            assert limiter.allow_message("user-6") is True


# ── Connection tracking ───────────────────────────────────────────────────────

class TestConnectionTracking:

    def test_first_connection_allowed(self, limiter, mock_redis):
        assert limiter.allow_connection("user-10") is True

    def test_connections_within_limit_allowed(self, limiter, mock_redis):
        for _ in range(MAX_CONNECTIONS_PER_USER - 1):
            limiter.register_connection("user-11")
        assert limiter.allow_connection("user-11") is True

    def test_connection_at_limit_blocked(self, limiter, mock_redis):
        for _ in range(MAX_CONNECTIONS_PER_USER):
            limiter.register_connection("user-12")
        assert limiter.allow_connection("user-12") is False

    def test_release_decrements_count(self, limiter, mock_redis):
        limiter.register_connection("user-13")
        limiter.register_connection("user-13")
        count_before = limiter.get_connection_count("user-13")
        limiter.release_connection("user-13")
        count_after = limiter.get_connection_count("user-13")
        assert count_after == count_before - 1

    def test_release_never_goes_below_zero(self, limiter, mock_redis):
        # Release without registering
        limiter.release_connection("user-14")
        assert limiter.get_connection_count("user-14") == 0

    def test_different_users_independent_connections(self, limiter, mock_redis):
        for _ in range(MAX_CONNECTIONS_PER_USER):
            limiter.register_connection("user-15")
        # user-16 unaffected
        assert limiter.allow_connection("user-16") is True

    def test_fails_open_when_redis_down(self, limiter):
        """If Redis is unavailable, connections should be allowed (fail open)."""
        limiter._redis = None
        with patch("apps.messaging.ws_rate_limiter.get_redis_connection",
                   side_effect=Exception("Redis down")):
            assert limiter.allow_connection("user-17") is True
