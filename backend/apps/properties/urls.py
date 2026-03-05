# apps/properties/urls.py
from django.urls import path
from .views import MyListingsView, PropertyCreateView, PropertyDetailView, PropertyListView, PropertyUpdateView

urlpatterns = [
    path("",          PropertyListView.as_view(),   name="property-list"),
    path("create/",   PropertyCreateView.as_view(),  name="property-create"),
    path("mine/",     MyListingsView.as_view(),      name="property-mine"),
    path("<uuid:pk>/", PropertyDetailView.as_view(), name="property-detail"),
    path("<uuid:pk>/update/", PropertyUpdateView.as_view(), name="property-update"),
]