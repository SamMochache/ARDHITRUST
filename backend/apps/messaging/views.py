# apps/messaging/views.py
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.pagination import StandardCursorPagination
from .models import Conversation, Message
from .serializers import ConversationCreateSerializer, ConversationSerializer, MessageSerializer


class ConversationListView(generics.ListAPIView):
    """GET /api/v1/messaging/conversations/ — user's conversations."""
    serializer_class   = ConversationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class   = StandardCursorPagination

    def get_queryset(self):
        user = self.request.user
        return (
            Conversation.objects
            .filter(Q(buyer=user) | Q(seller=user))
            .select_related("property", "buyer", "seller")
            .prefetch_related("messages")
            .order_by("-created_at")
        )


class ConversationCreateView(APIView):
    """POST /api/v1/messaging/conversations/ — start a conversation."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ConversationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from apps.properties.models import Property
        prop = Property.objects.get(id=serializer.validated_data["property_id"])

        if prop.seller == request.user:
            return Response(
                {"detail": "You cannot message yourself about your own listing."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        convo, created = Conversation.objects.get_or_create(
            property=prop,
            buyer=request.user,
            seller=prop.seller,
        )

        return Response(
            ConversationSerializer(convo, context={"request": request}).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class MessageListView(generics.ListAPIView):
    """GET /api/v1/messaging/conversations/<id>/messages/"""
    serializer_class   = MessageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class   = StandardCursorPagination

    def get_queryset(self):
        user = self.request.user
        convo_id = self.kwargs["pk"]
        return (
            Message.objects
            .filter(
                conversation_id=convo_id,
                conversation__in=Conversation.objects.filter(
                    Q(buyer=user) | Q(seller=user)
                ),
            )
            .select_related("sender")
            .order_by("created_at")
        )