from rest_framework.permissions import BasePermission

class IsKYCApproved(BasePermission):
    message = "KYC verification required."
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "kyc")
            and request.user.kyc.status == "APPROVED"
        )

class IsVerifiedSeller(IsKYCApproved):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == "SELLER"

class IsPropertyOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.seller == request.user