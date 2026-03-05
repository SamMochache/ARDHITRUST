# apps/messaging/models.py
import uuid
from django.db import models
from encrypted_model_fields.fields import EncryptedTextField

class Conversation(models.Model):
    id       = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey("properties.Property", on_delete=models.PROTECT)
    buyer    = models.ForeignKey("accounts.CustomUser", on_delete=models.PROTECT,
                                  related_name="buyer_conversations")
    seller   = models.ForeignKey("accounts.CustomUser", on_delete=models.PROTECT,
                                  related_name="seller_conversations")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("property", "buyer", "seller")]

class Message(models.Model):
    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation    = models.ForeignKey(Conversation, on_delete=models.CASCADE,
                                        related_name="messages")
    sender          = models.ForeignKey("accounts.CustomUser", on_delete=models.PROTECT)
    body_encrypted  = EncryptedTextField()
    read_at         = models.DateTimeField(null=True, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)