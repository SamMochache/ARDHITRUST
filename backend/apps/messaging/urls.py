# apps/messaging/urls.py
from django.urls import path
from .views import ConversationCreateView, ConversationListView, MessageListView

urlpatterns = [
    path("conversations/",             ConversationListView.as_view(),  name="conversation-list"),
    path("conversations/create/",      ConversationCreateView.as_view(), name="conversation-create"),
    path("conversations/<uuid:pk>/messages/", MessageListView.as_view(), name="message-list"),
]