# apps/services/views.py
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsKYCApproved
from apps.properties.models import Property
from .models import Quote, ServiceRequest


class ServiceRequestCreateView(APIView):
    """POST /api/v1/services/request/ — request a valuation, survey, or due diligence."""
    permission_classes = [IsKYCApproved]

    def post(self, request):
        property_id  = request.data.get("property_id")
        service_type = request.data.get("service_type")
        notes        = request.data.get("notes", "")

        if service_type not in ["VALUATION", "SURVEY", "DUE_DILIGENCE"]:
            return Response({"detail": "Invalid service_type."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            prop = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            return Response({"detail": "Property not found."}, status=status.HTTP_404_NOT_FOUND)

        req = ServiceRequest.objects.create(
            property=prop,
            requester=request.user,
            service_type=service_type,
            notes=notes,
        )
        return Response({
            "id":           str(req.id),
            "service_type": req.service_type,
            "status":       req.status,
        }, status=status.HTTP_201_CREATED)


class QuoteSubmitView(APIView):
    """POST /api/v1/services/quotes/ — service provider submits quote."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from apps.accounts.models import UserRole
        if request.user.role not in [UserRole.VALUER, UserRole.SURVEYOR]:
            return Response({"detail": "Only valuers and surveyors can submit quotes."},
                            status=status.HTTP_403_FORBIDDEN)

        req_id     = request.data.get("request_id")
        amount_kes = request.data.get("amount_kes")
        details    = request.data.get("details", "")
        est_days   = request.data.get("estimated_days", 7)

        try:
            req = ServiceRequest.objects.get(id=req_id, status="OPEN")
        except ServiceRequest.DoesNotExist:
            return Response({"detail": "Service request not found or already quoted."},
                            status=status.HTTP_404_NOT_FOUND)

        quote = Quote.objects.create(
            request=req,
            provider=request.user,
            amount_kes=amount_kes,
            details=details,
            estimated_days=est_days,
        )
        return Response({
            "id":            str(quote.id),
            "amount_kes":    quote.amount_kes,
            "estimated_days": quote.estimated_days,
        }, status=status.HTTP_201_CREATED)