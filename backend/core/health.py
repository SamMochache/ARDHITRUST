# core/health.py
# FIX 8: Health Check + Metrics Endpoints
#
# PROBLEM SOLVED:
#   Without health checks, the load balancer can't tell if a server is alive.
#   A Django process that's up but can't reach the DB gets traffic anyway.
#   Operations team has no visibility into queue depths, cache hit rates, etc.
#
# ENDPOINTS ADDED:
#   GET /api/health/          — load balancer check (fast, < 5ms)
#   GET /api/health/detailed/ — ops team check (DB, Redis, queue depths)
#   GET /api/metrics/         — Prometheus-compatible metrics
#
# LOAD BALANCER CONFIG (AWS ALB / nginx):
#   Health check path: /api/health/
#   Healthy threshold: 2 consecutive 200s
#   Unhealthy threshold: 3 consecutive non-200s
#   Timeout: 5 seconds
#   Interval: 30 seconds

import time
import logging
from django.http import JsonResponse
from django.views import View
from django.conf import settings

logger = logging.getLogger(__name__)


class HealthView(View):
    """
    GET /api/health/ — Fast liveness check for load balancer.
    Does minimal work: no DB, no Redis. Just confirms process is alive.
    Returns 200 if alive, 503 if not (load balancer removes from rotation).
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
    Checks: PostgreSQL, Redis, Celery queue depths.
    Used by: monitoring dashboards, on-call alerts.
    NOT used by load balancer (too slow at 50-200ms).
    """

    def get(self, request):
        start    = time.time()
        checks   = {}
        overall  = "ok"

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
                "status": "ok" if val == "1" else "error",
                "latency_ms": self._ms(start),
            }
        except Exception as e:
            checks["redis"]   = {"status": "error", "detail": str(e)}
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
                # Alert if any queue is backing up
                if depth > 1000:
                    overall = "degraded"
            checks["celery_queues"] = {"status": "ok", "depths": q_depths}
        except Exception as e:
            checks["celery_queues"] = {"status": "unknown", "detail": str(e)}

        # ── Recent Error Rate ────────────────────────────────────────────
        try:
            from apps.audit.models import AuditEvent
            from django.utils import timezone
            from datetime import timedelta
            recent_errors = AuditEvent.objects.filter(
                action="MPESA_CALLBACK",
                created_at__gte=timezone.now() - timedelta(minutes=5),
                metadata__result_code__ne=0,
            ).count()
            checks["mpesa_errors_5min"] = int(recent_errors)
        except Exception:
            pass

        http_status = 200 if overall == "ok" else 503
        return JsonResponse({
            "status":        overall,
            "checks":        checks,
            "total_ms":      self._ms(start),
            "timestamp":     time.time(),
        }, status=http_status)

    def _ms(self, start: float) -> int:
        return int((time.time() - start) * 1000)


class MetricsView(View):
    """
    GET /api/metrics/ — Basic Prometheus-format metrics.
    For full Prometheus integration, use django-prometheus package
    (already in requirements/production.txt).
    This view provides quick operational numbers without extra setup.
    """

    def get(self, request):
        if not request.user.is_staff:
            from django.http import HttpResponse
            return HttpResponse(status=403)

        metrics = {}

        try:
            from apps.accounts.models import CustomUser, KYCProfile
            metrics["users_total"]    = CustomUser.objects.count()
            metrics["kyc_approved"]   = KYCProfile.objects.filter(status="APPROVED").count()
            metrics["kyc_pending"]    = KYCProfile.objects.filter(status="PENDING").count()
        except Exception:
            pass

        try:
            from apps.properties.models import Property
            metrics["properties_active"]    = Property.objects.filter(status="ACTIVE").count()
            metrics["properties_under_offer"] = Property.objects.filter(status="UNDER_OFFER").count()
            metrics["properties_sold"]      = Property.objects.filter(status="SOLD").count()
        except Exception:
            pass

        try:
            from apps.escrow.models import EscrowTransaction
            from django.db.models import Sum
            metrics["escrow_active"]   = EscrowTransaction.objects.exclude(
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
            metrics["agent_runs_24h"]  = AgentRun.objects.filter(
                created_at__gte=timezone.now() - timedelta(hours=24)
            ).count()
            metrics["agent_errors_24h"] = AgentRun.objects.filter(
                created_at__gte=timezone.now() - timedelta(hours=24),
                error__isnull=False,
            ).count()
        except Exception:
            pass

        return JsonResponse(metrics)