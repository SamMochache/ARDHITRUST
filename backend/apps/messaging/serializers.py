# apps/messaging/serializers.py
from rest_framework import serializers
from .models import Conversation, Message


class ConversationSerializer(serializers.ModelSerializer):
    property_title = serializers.SerializerMethodField()
    other_party    = serializers.SerializerMethodField()
    last_message   = serializers.SerializerMethodField()

    class Meta:
        model  = Conversation
        fields = ["id", "property_title", "other_party", "last_message", "created_at"]

    def get_property_title(self, obj): return obj.property.title

    def get_other_party(self, obj):
        request = self.context.get("request")
        if not request:
            return None
        user = request.user
        other = obj.seller if obj.buyer == user else obj.buyer
        return {"id": str(other.id), "name": other.get_full_name()}

    def get_last_message(self, obj):
        msg = obj.messages.order_by("-created_at").first()
        if msg:
            return {"timestamp": msg.created_at.isoformat()}
        return None


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()

    class Meta:
        model  = Message
        fields = ["id", "sender_name", "body_encrypted", "read_at", "created_at"]
        # body_encrypted is decrypted transparently by django-encrypted-model-fields

    def get_sender_name(self, obj): return obj.sender.get_full_name()


class ConversationCreateSerializer(serializers.Serializer):
    property_id = serializers.UUIDField()

    def validate_property_id(self, value):
        from apps.properties.models import Property
        try:
            Property.objects.get(id=value, status="ACTIVE")
        except Property.DoesNotExist:
            raise serializers.ValidationError("Property not found or not active.")
        return value