# apps/messaging/tests_ws_rate_limiter.py
# FIX: Updated fail-open tests to patch the correct module-level target.
#
# PROBLEM:
#   Previous tests patched "apps.messaging.ws_rate_limiter.get_redis_connection"
#   but the import was inside _get_redis() — a local import — so the patch
#   target didn't exist in the module namespace and mocks never fired.
#   With get_redis_connection now a module-level import, the patch target
#   resolves correctly and the fail-open tests actually test what they claim.
#
#   We also add an explicit test that verifies the patch target resolves —
#   i.e. that the mock actually intercepts the call rather than calling Redis.

import pytest
import time
from unittest.mock import patch, MagicMock
from apps.messaging.ws_rate_limiter import (
    WebSocketRateLimiter,
    RATE_LIMIT_MAX_MESSAGES,
    RATE_LIMIT_WINDOW_SECONDS,
    MAX_CONNECTIONS_PER_USER,
)

PATCH_TARGET = "apps.messaging.ws_rate_limiter.get_redis_connection"


@pytest.fixture
def limiter():
    return WebSocketRateLimiter()


@pytest.fixture
def mock_redis(limiter):
    """Inject fake Redis so tests run without a real Redis instance."""
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
                    store.setdefault(cmd[1], {})
                    results.append(None)
                elif cmd[0] == "zcard":
                    results.append(len(store.get(cmd[1], {})))
                elif cmd[0] == "zadd":
                    store.setdefault(cmd[1], {}).update(cmd[2])
                    results.append(1)
                elif cmd[0] == "expire":
                    results.append(True)
                elif cmd[0] == "incr":
                    key = cmd[1]
                    val = int(store.get(key, b"0")) + 1
                    store[key] = str(val).encode()
                    results.append(val)
            return results

    class FakeRedis:
        def pipeline(self): return FakePipeline()
        def get(self, key): return store.get(key)
        def incr(self, key):
            val = int(store.get(key, b"0")) + 1
            store[key] = str(val).encode()
            return val
        def decr(self, key):
            val = max(0, int(store.get(key, b"1")) - 1)
            store[key] = str(val).encode()
            return val
        def expire(self, key, ttl): return True
        def zremrangebyscore(self, key, mn, mx): store.setdefault(key, {})
        def zcard(self, key): return len(store.get(key, {}))

    fake = FakeRedis()
    limiter._redis = fake
    return fake, store


# ── Message rate limiting ──────────────────────────────────────────────────────

class TestMessageRateLimit:

    def test_first_message_allowed(self, limiter, mock_redis):
        assert limiter.allow_message("user-1") is True

    def test_messages_within_limit_allowed(self, limiter, mock_redis):
        for _ in range(RATE_LIMIT_MAX_MESSAGES - 1):
            assert limiter.allow_message("user-2") is True

    def test_message_at_limit_blocked(self, limiter, mock_redis):
        for _ in range(RATE_LIMIT_MAX_MESSAGES):
            limiter.allow_message("user-3")
        assert limiter.allow_message("user-3") is False

    def test_different_users_independent_limits(self, limiter, mock_redis):
        for _ in range(RATE_LIMIT_MAX_MESSAGES):
            limiter.allow_message("user-4")
        assert limiter.allow_message("user-5") is True

    def test_fails_open_when_redis_down(self, limiter):
        """
        Verifies the module-level patch target resolves correctly.
        If the import were still inside _get_redis(), this patch would
        be a no-op and the test would attempt a real Redis connection,
        raising a connection error rather than returning True.
        """
        limiter._redis = None  # force _get_redis() to call get_redis_connection
        with patch(PATCH_TARGET, side_effect=Exception("Redis down")):
            result = limiter.allow_message("user-6")
        assert result is True  # fail open

    def test_patch_target_is_intercepted(self, limiter):
        """
        Explicit test that the patch target actually intercepts the call.
        If get_redis_connection were a local import, mock.call_count would be 0.
        """
        limiter._redis = None
        mock_conn = MagicMock()
        mock_conn.pipeline.return_value.execute.return_value = [None, 0, 1, True]
        with patch(PATCH_TARGET, return_value=mock_conn) as mock_get:
            limiter.allow_message("user-patch-test")
        assert mock_get.call_count == 1  # patch was intercepted


# ── Connection tracking ────────────────────────────────────────────────────────

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
        assert limiter.get_connection_count("user-13") == count_before - 1

    def test_release_never_goes_below_zero(self, limiter, mock_redis):
        limiter.release_connection("user-14")
        assert limiter.get_connection_count("user-14") == 0

    def test_different_users_independent_connections(self, limiter, mock_redis):
        for _ in range(MAX_CONNECTIONS_PER_USER):
            limiter.register_connection("user-15")
        assert limiter.allow_connection("user-16") is True

    def test_fails_open_when_redis_down(self, limiter):
        """Same patch target verification — connection tracking path."""
        limiter._redis = None
        with patch(PATCH_TARGET, side_effect=Exception("Redis down")):
            result = limiter.allow_connection("user-17")
        assert result is True
