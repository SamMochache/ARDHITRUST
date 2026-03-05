# apps/properties/filters.py
import django_filters
from .models import Property, PropertyType, PropertyStatus


class PropertyFilter(django_filters.FilterSet):
    county         = django_filters.CharFilter(lookup_expr="iexact")
    property_type  = django_filters.ChoiceFilter(choices=PropertyType.choices)
    min_size       = django_filters.NumberFilter(field_name="size_acres", lookup_expr="gte")
    max_size       = django_filters.NumberFilter(field_name="size_acres", lookup_expr="lte")
    min_price      = django_filters.NumberFilter(field_name="price_kes",  lookup_expr="gte")
    max_price      = django_filters.NumberFilter(field_name="price_kes",  lookup_expr="lte")
    is_verified_pro = django_filters.BooleanFilter()
    min_trust_score = django_filters.NumberFilter(field_name="trust_score", lookup_expr="gte")

    class Meta:
        model  = Property
        fields = ["county", "property_type", "min_size", "max_size",
                  "min_price", "max_price", "is_verified_pro", "min_trust_score"]