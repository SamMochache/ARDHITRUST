# apps/properties/views.py
from rest_framework import generics, filters as drf_filters, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.audit.models import AuditEvent
from apps.accounts.permissions import IsKYCApproved, IsPropertyOwner, IsVerifiedSeller
from .models import Property, PropertyStatus
from .serializers import PropertyCreateSerializer, PropertyDetailSerializer, PropertyListSerializer
from .filters import PropertyFilter
from core.pagination import StandardCursorPagination


class PropertyListView(generics.ListAPIView):
    """GET /api/v1/properties/ — public listing with filters."""
    serializer_class   = PropertyListSerializer
    permission_classes = [AllowAny]
    pagination_class   = StandardCursorPagination
    filter_backends    = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class    = PropertyFilter
    search_fields      = ["title", "area_name", "county", "description"]
    ordering_fields    = ["price_kes", "size_acres", "created_at", "trust_score"]
    ordering           = ["-trust_score", "-created_at"]

    def get_queryset(self):
        return (
            Property.objects
            .select_related("seller")
            .filter(status=PropertyStatus.ACTIVE)
            .only(
                "id", "title", "area_name", "county", "price_kes",
                "size_acres", "property_type", "is_verified_pro",
                "trust_score", "last_verified_at", "status",
            )
        )


class PropertyCreateView(generics.CreateAPIView):
    """POST /api/v1/properties/ — create listing (KYC approved sellers only)."""
    serializer_class   = PropertyCreateSerializer
    permission_classes = [IsVerifiedSeller]

    def perform_create(self, serializer):
        prop = serializer.save()
        AuditEvent.log(
            actor=self.request.user, action="PROPERTY_CREATED",
            resource_type="Property", resource_id=str(prop.id),
            metadata={"title": prop.title, "county": prop.county},
        )


class PropertyDetailView(generics.RetrieveAPIView):
    """GET /api/v1/properties/<id>/ — public property detail."""
    serializer_class   = PropertyDetailSerializer
    permission_classes = [AllowAny]
    queryset           = Property.objects.select_related("seller").filter(
        status__in=[PropertyStatus.ACTIVE, PropertyStatus.UNDER_OFFER]
    )


class PropertyUpdateView(generics.UpdateAPIView):
    """PATCH /api/v1/properties/<id>/ — seller updates their listing."""
    serializer_class   = PropertyCreateSerializer
    permission_classes = [IsAuthenticated, IsPropertyOwner]
    http_method_names  = ["patch"]

    def get_queryset(self):
        return Property.objects.filter(seller=self.request.user)

    def perform_update(self, serializer):
        prop = serializer.save()
        AuditEvent.log(
            actor=self.request.user, action="PROPERTY_UPDATED",
            resource_type="Property", resource_id=str(prop.id),
        )


class MyListingsView(generics.ListAPIView):
    """GET /api/v1/properties/mine/ — seller's own listings (all statuses)."""
    serializer_class   = PropertyDetailSerializer
    permission_classes = [IsAuthenticated]
    pagination_class   = StandardCursorPagination

    def get_queryset(self):
        return Property.objects.filter(seller=self.request.user).order_by("-created_at")