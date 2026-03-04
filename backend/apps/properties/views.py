# apps/properties/views.py
from rest_framework import generics, filters as drf_filters
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import Property, PropertyStatus
from .serializers import PropertyListSerializer
from .filters import PropertyFilter
from core.pagination import StandardCursorPagination

class PropertyListView(generics.ListAPIView):
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