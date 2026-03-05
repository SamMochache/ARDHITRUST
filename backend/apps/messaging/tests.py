# apps/messaging/tests.py
import pytest
from apps.messaging.models import Conversation, Message

CONV_LIST_URL   = "/api/v1/messaging/conversations/"
CONV_CREATE_URL = "/api/v1/messaging/conversations/create/"


@pytest.mark.django_db
class TestConversations:
    def test_create(self, buyer_client, property_obj):
        r = buyer_client.post(CONV_CREATE_URL,
                              {"property_id": str(property_obj.id)})
        assert r.status_code == 201
        assert "id" in r.data

    def test_create_idempotent(self, buyer_client, property_obj):
        r1 = buyer_client.post(CONV_CREATE_URL, {"property_id": str(property_obj.id)})
        r2 = buyer_client.post(CONV_CREATE_URL, {"property_id": str(property_obj.id)})
        assert r1.status_code == 201
        assert r2.status_code == 200
        assert r1.data["id"] == r2.data["id"]

    def test_seller_cannot_message_own_listing(self, seller_client, property_obj):
        r = seller_client.post(CONV_CREATE_URL,
                               {"property_id": str(property_obj.id)})
        assert r.status_code == 400

    def test_list_shows_users_conversations(self, buyer_client, buyer, seller, property_obj):
        Conversation.objects.create(
            property=property_obj, buyer=buyer, seller=seller
        )
        r = buyer_client.get(CONV_LIST_URL)
        assert r.status_code == 200
        assert len(r.data["results"]) == 1

    def test_unauthenticated_blocked(self, api_client, property_obj):
        r = api_client.post(CONV_CREATE_URL, {"property_id": str(property_obj.id)})
        assert r.status_code == 401


@pytest.mark.django_db
class TestMessages:
    def test_list_messages(self, buyer_client, buyer, seller, property_obj):
        convo = Conversation.objects.create(
            property=property_obj, buyer=buyer, seller=seller
        )
        Message.objects.create(conversation=convo, sender=buyer, body_encrypted="Hello")
        r = buyer_client.get(f"{CONV_LIST_URL}{convo.id}/messages/")
        assert r.status_code == 200
        assert len(r.data["results"]) == 1

    def test_non_participant_gets_empty(self, buyer, seller, property_obj):
        from django.contrib.auth import get_user_model
        from rest_framework_simplejwt.tokens import RefreshToken
        from rest_framework.test import APIClient
        User = get_user_model()
        stranger = User.objects.create_user(
            email="s2@test.com", phone="0700000088",
            first_name="S", last_name="T", password="x",
        )
        convo = Conversation.objects.create(
            property=property_obj, buyer=buyer, seller=seller
        )
        c = APIClient()
        token = RefreshToken.for_user(stranger)
        c.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token.access_token)}")
        r = c.get(f"{CONV_LIST_URL}{convo.id}/messages/")
        assert r.status_code == 200
        assert len(r.data["results"]) == 0