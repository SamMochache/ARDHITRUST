# apps/accounts/views.py
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.audit.models import AuditEvent
from .models import KYCProfile
from .serializers import KYCStatusSerializer, KYCSubmitSerializer, RegisterSerializer, UserSerializer
from .tasks import process_kyc_submission


class RegisterView(generics.CreateAPIView):
    """POST /api/v1/auth/register/ — create account, auto-creates KYC profile."""
    serializer_class   = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        AuditEvent.log(
            actor=user, action="USER_REGISTERED",
            resource_type="CustomUser", resource_id=str(user.id),
            metadata={"email": user.email, "role": user.role},
        )

        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )


class MeView(generics.RetrieveAPIView):
    """GET /api/v1/auth/me/ — current user profile."""
    serializer_class   = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class KYCSubmitView(APIView):
    """POST /api/v1/auth/kyc/submit/ — submit KYC documents."""
    permission_classes = [IsAuthenticated]
    # Rate-limited to 5/min via DRF throttle class in settings

    def post(self, request):
        serializer = KYCSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        kyc = request.user.kyc
        if kyc.status == KYCProfile.Status.APPROVED:
            return Response(
                {"detail": "KYC already approved."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Store PII encrypted
        request.user.national_id_encrypted = data["national_id"]
        request.user.save(update_fields=["national_id_encrypted"])

        kyc.kra_pin_encrypted = data["kra_pin"]
        kyc.id_front_s3_key   = data["id_front_key"]
        kyc.id_back_s3_key    = data["id_back_key"]
        kyc.status            = KYCProfile.Status.PENDING
        kyc.submitted_at      = timezone.now()
        kyc.save()

        # Dispatch async verification
        process_kyc_submission.delay(str(kyc.id))

        AuditEvent.log(
            actor=request.user, action="KYC_SUBMITTED",
            resource_type="KYCProfile", resource_id=str(kyc.id),
        )

        return Response({"detail": "KYC submitted. Processing usually takes under 2 minutes."})


class KYCStatusView(generics.RetrieveAPIView):
    """GET /api/v1/auth/kyc/status/ — check KYC status."""
    serializer_class   = KYCStatusSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.kyc