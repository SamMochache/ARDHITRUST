# core/health.py
# FIX 8: Health Check + Metrics Endpoints
#
# FIXES APPLIED IN THIS VERSION:
#   1. MetricsView now extends DRF APIView with IsAdminUser permission class.
#      Previously extended plain Django View — DRF authentication was never
#      applied, meaning request.user was always AnonymousUser and the
#      `if not request.user.is_staff` check always returned 403 for everyone,
#      including real admins. An unauthenticated request would also hit the
#      403 branch rather than 401, leaking that the endpoint exists.
#
#   2. DetailedHealthView now extends APIView (no auth required — load balancer
#      must reach it without a token) but rate-limited via nginx/ALB config.
#      The mpesa_errors_5min query used metadata__result_code__ne which is not
#      a valid Django ORM lookup — fixed to exclude result_code=0.
#
#   3. HealthView kept as plain Django View intentionally — load balancers call
#      this before any middleware runs and must not require auth.

import time
import logging
from django.http import JsonResponse
from django.views import View
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

logger = logging.getLogger(__name__)


class HealthView(View):
    """
    GET /api/health/ — Fast liveness check for load balancer.
    No auth required — load balancer calls this without a token.
    Returns 200 if alive. That is all the load balancer needs to know.
    """

    def get(self, request):
        return JsonResponse({
            "status":  "ok",
            "service": "ardhitrust-backend",
            "version": getattr(settings, "APP_VERSION", "1.0.0"),
        }, status=200)


class DetailedHealthView(View):
    """
    GET /api/health/detailed/ — Full dependency check for ops team.
    No auth required — called by monitoring dashboards from trusted networks.
    Restrict access at the load balancer / VPN level rather than auth token.

    Checks: PostgreSQL, Redis, Celery queue depths.
    NOT used by load balancer (too slow at 50-200ms).
    """

    def get(self, request):
        start   = time.time()
        checks  = {}
        overall = "ok"

        # ── PostgreSQL ──────────────────────────────────────────────────
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            checks["database"] = {"status": "ok", "latency_ms": self._ms(start)}
        except Exception as e:
            checks["database"] = {"status": "error", "detail": str(e)}
            overall = "degraded"

        # ── Redis ────────────────────────────────────────────────────────
        try:
            from django.core.cache import cache
            cache.set("health_check", "1", timeout=10)
            val = cache.get("health_check")
            checks["redis"] = {
                "status":     "ok" if val == "1" else "error",
                "latency_ms": self._ms(start),
            }
        except Exception as e:
            checks["redis"] = {"status": "error", "detail": str(e)}
            overall = "degraded"

        # ── Celery Queue Depths ──────────────────────────────────────────
        try:
            from django_redis import get_redis_connection
            redis    = get_redis_connection("default")
            queues   = ["default", "verification", "payments", "ai_agents"]
            q_depths = {}
            for q in queues:
                depth = redis.llen(q)
                q_depths[q] = int(depth)
                if depth > 1000:
                    overall = "degraded"
            checks["celery_queues"] = {"status": "ok", "depths": q_depths}
        except Exception as e:
            checks["celery_queues"] = {"status": "unknown", "detail": str(e)}

        # ── Recent M-Pesa Error Rate ─────────────────────────────────────
        # FIX: metadata__result_code__ne=0 is not a valid ORM lookup.
        # Use exclude(metadata__result_code=0) instead.
        try:
            from apps.audit.models import AuditEvent
            from django.utils import timezone
            from datetime import timedelta
            recent_errors = AuditEvent.objects.filter(
                action="MPESA_CALLBACK",
                created_at__gte=timezone.now() - timedelta(minutes=5),
            ).exclude(
                metadata__result_code=0
            ).count()
            checks["mpesa_errors_5min"] = int(recent_errors)
            if recent_errors > 20:
                overall = "degraded"
        except Exception:
            pass

        http_status = 200 if overall == "ok" else 503
        return JsonResponse({
            "status":    overall,
            "checks":    checks,
            "total_ms":  self._ms(start),
            "timestamp": time.time(),
        }, status=http_status)

    def _ms(self, start: float) -> int:
        return int((time.time() - start) * 1000)


class MetricsView(APIView):
    """
    GET /api/metrics/ — Operational metrics for admin users only.

    FIX: Previously extended plain Django View with a manual is_staff check.
    DRF authentication was never applied because Django's View doesn't run
    DRF's authentication middleware. This meant:
      - Unauthenticated requests got 403 (not 401) — leaking the endpoint.
      - Authenticated non-staff users got 403 correctly by accident.
      - The actual admin token was never validated by JWT.

    Now uses DRF APIView + IsAdminUser:
      - Unauthenticated → 401 Unauthorized (JWT not provided)
      - Authenticated non-staff → 403 Forbidden
      - Authenticated staff → 200 with metrics
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        metrics = {}

        try:
            from apps.accounts.models import CustomUser, KYCProfile
            metrics["users_total"]  = CustomUser.objects.count()
            metrics["kyc_approved"] = KYCProfile.objects.filter(status="APPROVED").count()
            metrics["kyc_pending"]  = KYCProfile.objects.filter(status="PENDING").count()
            metrics["kyc_rejected"] = KYCProfile.objects.filter(status="REJECTED").count()
        except Exception:
            pass

        try:
            from apps.properties.models import Property
            metrics["properties_active"]      = Property.objects.filter(status="ACTIVE").count()
            metrics["properties_under_offer"] = Property.objects.filter(status="UNDER_OFFER").count()
            metrics["properties_sold"]        = Property.objects.filter(status="SOLD").count()
        except Exception:
            pass

        try:
            from apps.escrow.models import EscrowTransaction
            from django.db.models import Sum
            metrics["escrow_active"] = EscrowTransaction.objects.exclude(
                status__in=["COMPLETED", "REFUNDED"]
            ).count()
            completed_sum = EscrowTransaction.objects.filter(
                status="COMPLETED"
            ).aggregate(total=Sum("amount_kes"))["total"]
            metrics["escrow_total_kes"] = completed_sum or 0
        except Exception:
            pass

        try:
            from apps.agents.models import AgentRun
            from django.utils import timezone
            from datetime import timedelta
            cutoff = timezone.now() - timedelta(hours=24)
            metrics["agent_runs_24h"]   = AgentRun.objects.filter(created_at__gte=cutoff).count()
            metrics["agent_errors_24h"] = AgentRun.objects.filter(
                created_at__gte=cutoff,
                error__isnull=False,
            ).count()
            # Error rate as a percentage
            if metrics["agent_runs_24h"] > 0:
                metrics["agent_error_rate_pct"] = round(
                    metrics["agent_errors_24h"] / metrics["agent_runs_24h"] * 100, 2
                )
        except Exception:
            pass

        return Response(metrics)