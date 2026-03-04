import httpx
from dataclasses import dataclass
from django.conf import settings
from core.exceptions import ExternalServiceError

@dataclass
class IPRSResult:
    verified: bool
    message: str

class IPRSService:
    def verify(self, national_id: str, first_name: str, last_name: str) -> IPRSResult:
        if settings.IPRS_MOCK_MODE:
            return IPRSResult(verified=True, message="Mock")

        try:
            r = httpx.post(
                f"{settings.IPRS_API_URL}/verify",
                json={"national_id": national_id, "first_name": first_name, "last_name": last_name},
                headers={"Authorization": f"Bearer {settings.IPRS_API_KEY}"},
                timeout=30.0,
            )
            r.raise_for_status()
            data = r.json()
            return IPRSResult(verified=data.get("verified", False), message=data.get("message", ""))
        except httpx.TimeoutException:
            raise ExternalServiceError("IPRS API timeout.")
        except httpx.HTTPStatusError as e:
            raise ExternalServiceError(f"IPRS error: {e.response.status_code}")