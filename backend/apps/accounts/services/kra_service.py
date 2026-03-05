# apps/accounts/services/kra_service.py
import httpx
from dataclasses import dataclass
from django.conf import settings
from core.exceptions import ExternalServiceError


@dataclass
class KRAResult:
    verified: bool
    message: str


class KRAService:
    def verify(self, kra_pin: str, national_id: str) -> KRAResult:
        if settings.IPRS_MOCK_MODE:  # shares mock flag for development
            return KRAResult(verified=True, message="Mock KRA verification")

        try:
            r = httpx.post(
                f"{settings.KRA_API_URL}/verify-pin",
                json={"kra_pin": kra_pin, "national_id": national_id},
                headers={"Authorization": f"Bearer {settings.KRA_API_KEY}"},
                timeout=30.0,
            )
            r.raise_for_status()
            data = r.json()
            return KRAResult(
                verified=data.get("valid", False),
                message=data.get("message", ""),
            )
        except httpx.TimeoutException:
            raise ExternalServiceError("KRA API timeout.")
        except httpx.HTTPStatusError as e:
            raise ExternalServiceError(f"KRA API error: {e.response.status_code}")