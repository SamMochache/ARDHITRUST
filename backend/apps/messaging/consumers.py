# apps/messaging/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.room = f"chat_{self.conversation_id}"
        user = self.scope["user"]

        if not user.is_authenticated:
            await self.close(code=4001)
            return
        if not await self._is_participant(user, self.conversation_id):
            await self.close(code=4003)
            return

        await self.channel_layer.group_add(self.room, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        body = data.get("message", "").strip()
        if not body or len(body) > 2000:
            return

        user    = self.scope["user"]
        saved   = await self._save_message(user, self.conversation_id, body)

        await self.channel_layer.group_send(self.room, {
            "type": "chat_message",
            "message": saved["body"],
            "sender_id": str(user.id),
            "sender_name": user.get_full_name(),
            "timestamp": saved["timestamp"],
            "message_id": saved["id"],
        })

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def _is_participant(self, user, conversation_id):
        from apps.messaging.models import Conversation
        from django.db.models import Q
        return Conversation.objects.filter(
            id=conversation_id
        ).filter(Q(buyer=user) | Q(seller=user)).exists()

    @database_sync_to_async
    def _save_message(self, user, conversation_id, body):
        from apps.messaging.models import Message, Conversation
        conv = Conversation.objects.get(id=conversation_id)
        msg  = Message.objects.create(
            conversation=conv, sender=user, body_encrypted=body
        )
        return {"id": str(msg.id), "body": body, "timestamp": msg.created_at.isoformat()}