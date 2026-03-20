# apps/messaging/consumers.py
#
# FIX: WebSocket rate limiting and connection tracking added.
#
# PROBLEMS SOLVED:
#   1. No rate limiting — one user could flood the channel with unlimited
#      messages per second, exhausting DB connections and Redis channel layer.
#   2. No connection limit — same user could open hundreds of parallel
#      WebSocket connections, each holding a channel layer subscription.
#   3. Silent failures — DB errors in _save_message were swallowed, making
#      it impossible to distinguish a successful send from a failed one.
#   4. Silent rate limit drops — messages that exceeded a hypothetical limit
#      would be dropped with no feedback to the client.
#
# CHANGES:
#   - WebSocketRateLimiter injected into the consumer
#   - allow_connection() checked on connect → close(4029) if over limit
#   - register_connection() called after successful connect
#   - release_connection() called in disconnect (always runs)
#   - allow_message() checked on every receive → error frame sent if over limit
#   - _save_message errors now raise instead of swallowing → error frame sent
#   - _send_error() helper sends a structured error frame to the client
#
# CLOSE CODES:
#   4001 — unauthenticated
#   4003 — not a conversation participant
#   4029 — too many connections (rate limit, mirrors HTTP 429)
#
# ERROR FRAME FORMAT (sent as JSON text):
#   { "type": "error", "code": "RATE_LIMITED" | "SAVE_FAILED", "message": "..." }

import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from .ws_rate_limiter import WebSocketRateLimiter

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):

    # Shared limiter instance — stateless, safe to share across consumers
    _limiter = WebSocketRateLimiter()

    async def connect(self):
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.room            = f"chat_{self.conversation_id}"
        user                 = self.scope["user"]
        self.user_id         = None  # set after auth check

        # ── Auth ──────────────────────────────────────────────────────────────
        if not user.is_authenticated:
            await self.close(code=4001)
            return

        if not await self._is_participant(user, self.conversation_id):
            await self.close(code=4003)
            return

        # ── Connection limit ──────────────────────────────────────────────────
        user_id_str = str(user.id)
        if not self._limiter.allow_connection(user_id_str):
            logger.warning(
                f"WebSocket connection rejected: user {user_id_str} "
                f"exceeded MAX_CONNECTIONS_PER_USER"
            )
            await self.close(code=4029)
            return

        # ── Accept and register ───────────────────────────────────────────────
        self.user_id = user_id_str
        await self.channel_layer.group_add(self.room, self.channel_name)
        await self.accept()
        self._limiter.register_connection(self.user_id)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room, self.channel_name)
        # Always release — even if connect was rejected before registration,
        # user_id is None so release_connection is safely skipped.
        if self.user_id:
            self._limiter.release_connection(self.user_id)

    async def receive(self, text_data):
        user = self.scope["user"]

        # ── Parse ─────────────────────────────────────────────────────────────
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self._send_error("INVALID_JSON", "Message must be valid JSON.")
            return

        body = data.get("message", "").strip()

        # ── Validate ──────────────────────────────────────────────────────────
        if not body:
            return  # silently ignore empty messages

        if len(body) > 2000:
            await self._send_error(
                "MESSAGE_TOO_LONG",
                "Message exceeds 2000 character limit.",
            )
            return

        # ── Rate limit ────────────────────────────────────────────────────────
        if not self._limiter.allow_message(str(user.id)):
            logger.warning(
                f"WebSocket rate limit exceeded: user={user.id} "
                f"conversation={self.conversation_id}"
            )
            await self._send_error(
                "RATE_LIMITED",
                "You are sending messages too quickly. Please slow down.",
            )
            return

        # ── Persist ───────────────────────────────────────────────────────────
        try:
            saved = await self._save_message(user, self.conversation_id, body)
        except Exception as e:
            logger.exception(
                f"WebSocket _save_message failed: user={user.id} "
                f"conversation={self.conversation_id} error={e}"
            )
            await self._send_error(
                "SAVE_FAILED",
                "Your message could not be saved. Please try again.",
            )
            return

        # ── Broadcast ─────────────────────────────────────────────────────────
        await self.channel_layer.group_send(
            self.room,
            {
                "type":        "chat_message",
                "message":     saved["body"],
                "sender_id":   str(user.id),
                "sender_name": user.get_full_name(),
                "timestamp":   saved["timestamp"],
                "message_id":  saved["id"],
            },
        )

    async def chat_message(self, event):
        """Receive a broadcast and forward to this WebSocket client."""
        await self.send(text_data=json.dumps(event))

    # ── Helpers ───────────────────────────────────────────────────────────────

    async def _send_error(self, code: str, message: str) -> None:
        """
        Send a structured error frame to this client only (not broadcast).
        The client should display or log this — not retry automatically.
        """
        await self.send(text_data=json.dumps({
            "type":    "error",
            "code":    code,
            "message": message,
        }))

    @database_sync_to_async
    def _is_participant(self, user, conversation_id) -> bool:
        from apps.messaging.models import Conversation
        from django.db.models import Q
        return Conversation.objects.filter(
            id=conversation_id
        ).filter(
            Q(buyer=user) | Q(seller=user)
        ).exists()

    @database_sync_to_async
    def _save_message(self, user, conversation_id, body) -> dict:
        """
        Save message to DB and return serializable dict.
        Raises on any DB error — caller handles and sends error frame.
        """
        from apps.messaging.models import Message, Conversation
        conv = Conversation.objects.get(id=conversation_id)
        msg  = Message.objects.create(
            conversation=conv,
            sender=user,
            body_encrypted=body,
        )
        return {
            "id":        str(msg.id),
            "body":      body,
            "timestamp": msg.created_at.isoformat(),
        }
