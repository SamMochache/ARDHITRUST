# apps/agents/views.py
import uuid
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsKYCApproved
from apps.properties.models import Property
from .buyer_assistant_agent import BuyerAssistantAgent
from .title_intelligence_agent import TitleIntelligenceAgent


class BuyerAssistantView(APIView):
    """POST /api/v1/agents/assistant/ — chat with AI land buying assistant."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        message     = request.data.get("message", "").strip()
        session_key = request.data.get("session_key") or str(uuid.uuid4())
        property_id = request.data.get("property_id")

        if not message:
            return Response({"detail": "message required."}, status=status.HTTP_400_BAD_REQUEST)
        if len(message) > 2000:
            return Response({"detail": "Message too long (max 2000 chars)."}, status=status.HTTP_400_BAD_REQUEST)

        property_context = None
        if property_id:
            try:
                prop = Property.objects.get(id=property_id)
                property_context = {
                    "title": prop.title, "county": prop.county,
                    "property_type": prop.property_type,
                    "size_acres": float(prop.size_acres),
                    "price_kes": prop.price_kes,
                    "trust_score": prop.trust_score,
                    "status": prop.status,
                }
            except Property.DoesNotExist:
                pass

        agent  = BuyerAssistantAgent()
        result = agent.chat(
            user_message=message,
            session_key=f"{request.user.id}:{session_key}",
            property_context=property_context,
        )
        return Response(result)


class ValuationView(APIView):
    """POST /api/v1/agents/valuation/ — AI property valuation estimate."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        property_id = request.data.get("property_id")
        if not property_id:
            return Response({"detail": "property_id required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            prop = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            return Response({"detail": "Property not found."}, status=status.HTTP_404_NOT_FOUND)

        # Return cached AgentRun if available
        from apps.agents.models import AgentRun
        cached = (
            AgentRun.objects
            .filter(agent_name="ValuationAgent", property_id=property_id, error=None)
            .order_by("-created_at")
            .first()
        )
        if cached:
            return Response(cached.output_json)

        # Stub response until ValuationAgent is wired up
        return Response({
            "property_id": str(prop.id),
            "estimated_min_kes": int(prop.price_kes * 0.85),
            "estimated_max_kes": int(prop.price_kes * 1.15),
            "confidence": "LOW",
            "note": "Full AI valuation coming soon. Estimate based on listed price ±15%.",
        })