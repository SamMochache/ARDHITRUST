import httpx, base64
from datetime import datetime
from django.conf import settings

class MpesaClient:
    BASE = (
        "https://api.safaricom.co.ke"
        if settings.MPESA_ENV == "production"
        else "https://sandbox.safaricom.co.ke"
    )

    def _token(self) -> str:
        creds = base64.b64encode(
            f"{settings.MPESA_CONSUMER_KEY}:{settings.MPESA_CONSUMER_SECRET}".encode()
        ).decode()
        r = httpx.get(
            f"{self.BASE}/oauth/v1/generate?grant_type=client_credentials",
            headers={"Authorization": f"Basic {creds}"},
            timeout=30,
        )
        r.raise_for_status()
        return r.json()["access_token"]

    def stk_push(self, phone: str, amount: int, account_ref: str, desc: str) -> dict:
        ts  = datetime.now().strftime("%Y%m%d%H%M%S")
        raw = f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{ts}"
        pwd = base64.b64encode(raw.encode()).decode()

        r = httpx.post(
            f"{self.BASE}/mpesa/stkpush/v1/processrequest",
            json={
                "BusinessShortCode": settings.MPESA_SHORTCODE,
                "Password": pwd, "Timestamp": ts,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": amount,
                "PartyA": phone, "PartyB": settings.MPESA_SHORTCODE,
                "PhoneNumber": phone,
                "CallBackURL": f"{settings.BASE_URL}/api/v1/escrow/mpesa/callback/",
                "AccountReference": account_ref[:12],
                "TransactionDesc": desc[:13],
            },
            headers={"Authorization": f"Bearer {self._token()}"},
            timeout=30,
        )
        r.raise_for_status()
        return r.json()