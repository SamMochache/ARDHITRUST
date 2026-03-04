import httpx
from dataclasses import dataclass, field
from typing import Optional
from django.conf import settings
from django.core.cache import cache
from core.exceptions import ExternalServiceError

@dataclass
class ArdhisasaResult:
    ownership_confirmed: bool
    registered_owner: str
    encumbrances: list = field(default_factory=list)
    caveat_present: bool = False
    rates_cleared: bool = True
    error: Optional[str] = None

class ArdhisasaClient:
    def land_search(self, lr_number: str) -> ArdhisasaResult:
        if settings.ARDHISASA_MOCK_MODE:
            return ArdhisasaResult(
                ownership_confirmed=True,
                registered_owner="JOHN DOE MWANGI",
                rates_cleared=True,
            )

        cache_key = f"ardhisasa:search:{lr_number}"
        if cached := cache.get(cache_key):
            return ArdhisasaResult(**cached)

        try:
            r = httpx.post(
                f"{settings.ARDHISASA_API_URL}/land-search",
                json={"lr_number": lr_number},
                headers={"Authorization": f"Bearer {settings.ARDHISASA_API_KEY}"},
                timeout=60.0,
            )
            r.raise_for_status()
            data = r.json()
            result = ArdhisasaResult(
                ownership_confirmed=data["ownership"]["confirmed"],
                registered_owner=data["ownership"]["registered_owner"],
                encumbrances=data.get("encumbrances", []),
                caveat_present=data.get("caveat_present", False),
                rates_cleared=data.get("rates_cleared", False),
            )
            cache.set(cache_key, result.__dict__, timeout=86400)  # 24h cache
            return result
        except httpx.TimeoutException:
            raise ExternalServiceError("Ardhisasa API timed out.")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return ArdhisasaResult(
                    ownership_confirmed=False,
                    registered_owner="",
                    error="LR Number not found in Ardhisasa registry",
                )
            raise