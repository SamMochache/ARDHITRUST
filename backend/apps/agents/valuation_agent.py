# apps/agents/valuation_agent.py
# FIX: ValuationAgent now extends BaseAgent for consistent logging.
#
# PROBLEM:
#   ValuationAgent created its own Anthropic client directly in
#   _generate_narrative() and had its own partial _log_run() that
#   duplicated BaseAgent infrastructure. It was the one remaining
#   agent outside the BaseAgent logging pattern, meaning:
#     - Token costs for narrative generation were invisible in AgentRun
#     - Narrative failures weren't captured with full error context
#     - No input caching for identical valuation requests
#
# ARCHITECTURE DECISION:
#   ValuationAgent has two distinct AI calls:
#     1. The hedonic model (pure Python, no LLM)
#     2. The narrative generation (LLM via Claude)
#
#   We split this cleanly: ValuationAgent handles the hedonic model
#   and orchestration. NarrativeAgent (a thin BaseAgent subclass)
#   handles the LLM call with full caching, logging, and fallback.
#
#   This means:
#     - Identical property inputs hit the NarrativeAgent cache
#     - Token costs are tracked per narrative call in AgentRun
#     - Fallback narratives are returned on API failure (not exceptions)
#     - ValuationAgent._log_run() removed — BaseAgent handles it via
#       NarrativeAgent, and the valuation result is logged by NarrativeAgent

import json
import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)

# Property type price multipliers relative to RESIDENTIAL baseline
PROPERTY_TYPE_MULTIPLIERS = {
    "RESIDENTIAL":  1.00,
    "COMMERCIAL":   2.50,
    "AGRICULTURAL": 0.35,
    "INDUSTRIAL":   1.80,
}

# Trust score adjustments
TRUST_SCORE_ADJUSTMENTS = {
    (80, 101): 1.05,
    (60, 80):  1.00,
    (40, 60):  0.90,
    (0, 40):   0.75,
}

MIN_COMPARABLES_HIGH_CONFIDENCE   = 20
MIN_COMPARABLES_MEDIUM_CONFIDENCE = 5


@dataclass
class ValuationResult:
    estimated_value_kes: int
    estimated_min_kes:   int
    estimated_max_kes:   int
    confidence:          str
    comparables_used:    int
    price_per_acre:      int
    methodology:         str
    narrative_en:        str
    narrative_sw:        str
    comparable_sales:    list = field(default_factory=list)


# ── Narrative Agent ────────────────────────────────────────────────────────────
# Thin BaseAgent subclass that owns the LLM call for narrative generation.
# Separated from ValuationAgent so caching, logging, and fallback all work
# through the standard BaseAgent infrastructure.

from .base_agent import BaseAgent


class _NarrativeAgent(BaseAgent):
    """
    Internal agent — generates human-readable valuation narratives.
    Not exposed via views directly; called by ValuationAgent.estimate().

    Separated from ValuationAgent so that:
      - Token costs are tracked in AgentRun per narrative call
      - Identical inputs (same property state) hit the cache
      - API failures return a clean fallback narrative, not an exception
    """
    agent_name = "_NarrativeAgent"
    max_tokens = 800

    def build_prompt(
        self,
        area_name: str,
        county: str,
        property_type: str,
        size_acres: float,
        trust_score: int,
        estimate: int,
        price_per_acre: int,
        confidence: str,
        comp_summary: str,
        listed_price: int,
        **kwargs,
    ) -> list[dict]:
        return [{
            "role": "user",
            "content": f"""You are a Kenyan land valuation expert writing for a first-time land buyer.

Property details:
- Location: {area_name}, {county}
- Type: {property_type}
- Size: {size_acres} acres
- Trust Score: {trust_score}/100
- Our valuation: KES {estimate:,}
- Price per acre: KES {price_per_acre:,}
- Confidence: {confidence} (based on {comp_summary})
- Listed price: KES {listed_price:,}

Write a 2-paragraph valuation narrative:
Paragraph 1 (English): Explain why this property is valued at KES {estimate:,},
mentioning location, size, property type, and title quality. Be honest about confidence level.
Paragraph 2 (Swahili): Same content in clear Swahili for Kenyan buyers.

Respond ONLY in this JSON format, no other text:
{{"narrative_en": "...", "narrative_sw": "..."}}"""
        }]

    def parse_response(self, text: str) -> dict:
        try:
            clean = text.strip().lstrip("```json").rstrip("```").strip()
            parsed = json.loads(clean)
            return {
                "narrative_en": parsed.get("narrative_en", ""),
                "narrative_sw": parsed.get("narrative_sw", ""),
            }
        except (json.JSONDecodeError, AttributeError):
            return self._fallback_output()

    def _fallback_output(self, **kwargs) -> dict:
        # kwargs contains the build_prompt args when called from BaseAgent
        county        = kwargs.get("county", "the county")
        property_type = kwargs.get("property_type", "property")
        estimate      = kwargs.get("estimate", 0)
        comparables   = kwargs.get("comp_summary", "available data")
        confidence    = kwargs.get("confidence", "LOW")
        return {
            "narrative_en": (
                f"This {property_type.lower()} property in {county} "
                f"is estimated at KES {estimate:,} based on {comparables}. "
                f"Confidence: {confidence}."
            ),
            "narrative_sw": (
                f"Mali hii ya {property_type.lower()} katika {county} "
                f"inakadiriwa KES {estimate:,} kulingana na {comparables}. "
                f"Uhakika: {confidence}."
            ),
        }


# ── Valuation Agent ────────────────────────────────────────────────────────────

class ValuationAgent:
    """
    Property valuation using hedonic pricing model + Claude narrative.
    The number comes from statistics. The explanation comes from Claude
    via _NarrativeAgent (which uses BaseAgent infrastructure for logging).
    """

    def __init__(self):
        self._narrative_agent = _NarrativeAgent()

    def estimate(self, property_obj) -> ValuationResult:
        comparables = self._find_comparables(property_obj)
        estimate, confidence, price_per_acre = self._hedonic_estimate(
            property_obj, comparables
        )

        margin  = {"HIGH": 0.10, "MEDIUM": 0.20, "LOW": 0.30}[confidence]
        min_val = int(estimate * (1 - margin))
        max_val = int(estimate * (1 + margin))

        comp_summary = (
            f"{len(comparables)} comparable properties in {property_obj.county}"
            if comparables else "no local comparable sales yet"
        )

        # LLM narrative via NarrativeAgent — full BaseAgent logging + caching
        narrative_result = self._narrative_agent.run(
            area_name     = property_obj.area_name,
            county        = property_obj.county,
            property_type = property_obj.property_type,
            size_acres    = float(property_obj.size_acres),
            trust_score   = property_obj.trust_score,
            estimate      = estimate,
            price_per_acre= price_per_acre,
            confidence    = confidence,
            comp_summary  = comp_summary,
            listed_price  = property_obj.price_kes,
            property_id   = str(property_obj.id),
        )

        return ValuationResult(
            estimated_value_kes = estimate,
            estimated_min_kes   = min_val,
            estimated_max_kes   = max_val,
            confidence          = confidence,
            comparables_used    = len(comparables),
            price_per_acre      = price_per_acre,
            methodology         = "hedonic_v1",
            narrative_en        = narrative_result.get("narrative_en", ""),
            narrative_sw        = narrative_result.get("narrative_sw", ""),
            comparable_sales    = [
                {"price_kes": c["price_kes"], "size_acres": float(c["size_acres"]),
                 "county": c["county"], "property_type": c["property_type"]}
                for c in comparables[:5]
            ],
        )

    def _find_comparables(self, property_obj) -> list:
        from apps.properties.models import Property
        from django.db.models import Q

        size      = float(property_obj.size_acres)
        size_min  = size * 0.5
        size_max  = size * 1.5
        prop_type = property_obj.property_type
        county    = property_obj.county

        queries = [
            Q(county__iexact=county, property_type=prop_type,
              size_acres__gte=size_min, size_acres__lte=size_max, status="SOLD"),
            Q(county__iexact=county, property_type=prop_type,
              size_acres__gte=size_min, size_acres__lte=size_max,
              status__in=["SOLD", "ACTIVE", "UNDER_OFFER"]),
            Q(county__iexact=county, property_type=prop_type,
              status__in=["SOLD", "ACTIVE", "UNDER_OFFER"]),
            Q(county__iexact=county, status__in=["SOLD", "ACTIVE", "UNDER_OFFER"]),
        ]

        for query in queries:
            comps = list(
                Property.objects
                .filter(query)
                .exclude(id=property_obj.id)
                .values("price_kes", "size_acres", "county", "property_type", "trust_score")
                .order_by("-created_at")[:50]
            )
            if len(comps) >= MIN_COMPARABLES_MEDIUM_CONFIDENCE:
                return comps

        return []

    def _hedonic_estimate(self, property_obj, comparables: list) -> tuple[int, str, int]:
        if not comparables:
            national_baselines = {
                "RESIDENTIAL":  2_000_000,
                "AGRICULTURAL":   200_000,
                "COMMERCIAL":   5_000_000,
                "INDUSTRIAL":   3_600_000,
            }
            price_per_acre = national_baselines.get(property_obj.property_type, 2_000_000)
            estimate       = int(price_per_acre * float(property_obj.size_acres))
            return estimate, "LOW", price_per_acre

        prices_per_acre = []
        for comp in comparables:
            if comp["size_acres"] and float(comp["size_acres"]) > 0:
                ppa = comp["price_kes"] / float(comp["size_acres"])
                prices_per_acre.append(ppa)

        if not prices_per_acre:
            return int(property_obj.price_kes * 1.0), "LOW", 0

        prices_per_acre.sort()
        trim    = max(1, len(prices_per_acre) // 10)
        trimmed = prices_per_acre[trim:-trim] if len(prices_per_acre) > 2 else prices_per_acre

        median_ppa = sorted(trimmed)[len(trimmed) // 2]

        type_mult  = PROPERTY_TYPE_MULTIPLIERS.get(property_obj.property_type, 1.0)
        comp_types = set(c["property_type"] for c in comparables)
        if len(comp_types) > 1 or property_obj.property_type not in comp_types:
            dominant_type = max(comp_types, key=lambda t: sum(
                1 for c in comparables if c["property_type"] == t
            ))
            dominant_mult = PROPERTY_TYPE_MULTIPLIERS.get(dominant_type, 1.0)
            median_ppa    = median_ppa * (type_mult / dominant_mult)

        trust_adjustment = 1.0
        for (low, high), adj in TRUST_SCORE_ADJUSTMENTS.items():
            if low <= property_obj.trust_score < high:
                trust_adjustment = adj
                break

        price_per_acre = int(median_ppa * trust_adjustment)
        estimate       = int(price_per_acre * float(property_obj.size_acres))

        if len(comparables) >= MIN_COMPARABLES_HIGH_CONFIDENCE:
            confidence = "HIGH"
        elif len(comparables) >= MIN_COMPARABLES_MEDIUM_CONFIDENCE:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"

        return estimate, confidence, price_per_acre
