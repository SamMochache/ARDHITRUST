# core/throttling.py
# FIX 4: Custom AI Agent Throttle
#
# PROBLEM SOLVED:
#   settings.py defines "ai_agent: 10/minute" but the generic UserRateThrottle
#   doesn't know about it. Every user could hammer the AI endpoint at 200/minute
#   (the default user rate) = catastrophic Anthropic API costs at scale.
#
#   At 1M users × 200 messages/minute = $360,000/hour in API costs.
#   With 10/minute limit = $18,000/hour max — still significant but bounded.
#
# FIX APPLIED:
#   AIAgentThrottle: 10 requests/minute per user for AI endpoints.
#   VerificationThrottle: 5 requests/minute for verification (government API limits).
#   KYCSubmitThrottle: 3 requests/hour — prevents KYC spam.
#   RegisterThrottle: 5 requests/hour per IP — prevents account creation spam.
#
# WIRE UP IN VIEWS:
#   class BuyerAssistantView(APIView):
#       throttle_classes = [AIAgentThrottle]
#
#   class ValuationView(APIView):
#       throttle_classes = [AIAgentThrottle]

from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class AIAgentThrottle(UserRateThrottle):
    """
    10 AI requests per minute per authenticated user.
    Applies to: BuyerAssistantView, ValuationView, title intelligence endpoint.
    At 1M users × 10/min = 10M requests/min max theoretical.
    In practice peak concurrent users is 1-5% of total = 10,000-50,000 users.
    50,000 × 10/min = 500,000 AI calls/min = ~$900/min = manageable with usage caps.
    """
    scope = "ai_agent"


class VerificationThrottle(UserRateThrottle):
    """
    5 verification requests per minute.
    Ardhisasa and IPRS government APIs have their own rate limits.
    This prevents one user from exhausting our API quota.
    """
    scope = "verification"


class KYCSubmitThrottle(UserRateThrottle):
    """
    3 KYC submissions per hour per user.
    Prevents KYC spam and reduces IPRS/KRA API costs.
    A legitimate user needs at most 2-3 submissions (initial + resubmission).
    """
    scope = "kyc_submit"
    rate  = "3/hour"

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        return self.cache_format % {
            "scope": self.scope,
            "ident": ident,
        }


class RegisterThrottle(AnonRateThrottle):
    """
    5 registration attempts per hour per IP address.
    Prevents bot account creation at scale.
    Legitimate users register once — this only affects abusers.
    """
    scope = "register"
    rate  = "5/hour"


class MpesaCallbackThrottle(AnonRateThrottle):
    """
    Safaricom's callback IPs are known. In production, also add IP allowlisting
    in nginx/ALB. This throttle is a backstop.
    10,000/minute accommodates legitimate callback volume from Safaricom.
    """
    scope = "mpesa_callback"
    rate  = "10000/minute"