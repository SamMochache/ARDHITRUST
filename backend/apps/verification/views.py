# apps/verification/views.py
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.properties.models import Property
from .models import VerificationRequest, VerificationResult
from .tasks import initiate_ardhisasa_check


class VerificationStatusView(APIView):
    """GET /api/v1/verification/<property_id>/status/"""
    permission_classes = [IsAuthenticated]

    def get(self, request, property_id):
        try:
            prop = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            return Response({"detail": "Property not found."}, status=status.HTTP_404_NOT_FOUND)

        req = (
            VerificationRequest.objects
            .filter(property=prop)
            .order_by("-created_at")
            .first()
        )
        if not req:
            return Response({"status": "NOT_STARTED", "trust_score": 0})

        result_data = {}
        try:
            r = req.result
            result_data = {
                "ownership_confirmed": r.ownership_confirmed,
                "registered_owner":    r.registered_owner,
                "caveat_present":      r.caveat_present,
                "rates_cleared":       r.rates_cleared,
                "encumbrances_count":  len(r.encumbrances_json),
            }
        except VerificationResult.DoesNotExist:
            pass

        return Response({
            "status":      req.status,
            "trust_score": prop.trust_score,
            "verified_at": prop.last_verified_at,
            "result":      result_data,
        })


class VerificationRequestView(APIView):
    """POST /api/v1/verification/request/ — trigger re-verification."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        property_id = request.data.get("property_id")
        if not property_id:
            return Response({"detail": "property_id required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            prop = Property.objects.get(id=property_id, seller=request.user)
        except Property.DoesNotExist:
            return Response({"detail": "Property not found."}, status=status.HTTP_404_NOT_FOUND)

        initiate_ardhisasa_check.delay(str(prop.id))
        return Response({"detail": "Re-verification initiated."})