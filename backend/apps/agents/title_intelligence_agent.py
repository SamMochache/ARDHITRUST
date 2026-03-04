# apps/agents/title_intelligence_agent.py
import json
from .base_agent import BaseAgent

SYSTEM = """You are a Kenyan land title verification expert. 
Analyse verification data and return a Trust Score and risk assessment.
Respond ONLY in valid JSON. No markdown, no preamble."""

class TitleIntelligenceAgent(BaseAgent):
    agent_name = "TitleIntelligenceAgent"
    max_tokens = 2048

    def build_prompt(self, property_data: dict, verification_result: dict, **kw) -> list[dict]:
        return [{
            "role": "user",
            "content": f"""{SYSTEM}

PROPERTY: {json.dumps(property_data, indent=2)}
VERIFICATION: {json.dumps(verification_result, indent=2)}

Trust Score criteria:
- Ownership confirmed:       +30 pts
- No encumbrances:           +20 pts  
- No caveats:                +25 pts
- Rates cleared:             +15 pts
- Ownership history clean:   +10 pts

Respond in this exact JSON:
{{
  "trust_score": <int 0-100>,
  "risk_level": "<LOW|MEDIUM|HIGH>",
  "flags": ["<flag>"],
  "summary_en": "<2 sentences English>",
  "summary_sw": "<2 sentences Swahili>",
  "recommendation": "<BUY_SAFE|REVIEW_FIRST|AVOID>"
}}"""
        }]

    def parse_response(self, text: str) -> dict:
        try:
            clean = text.strip().lstrip("```json").rstrip("```").strip()
            return json.loads(clean)
        except json.JSONDecodeError:
            return self._fallback_output()

    def _fallback_output(self, **kw) -> dict:
        return {
            "trust_score": 50, "risk_level": "MEDIUM",
            "flags": ["Automated analysis unavailable"],
            "summary_en": "Automated analysis unavailable. Please request manual review.",
            "summary_sw": "Uchambuzi hauwezi kufanywa. Omba mapitio ya mwongozo.",
            "recommendation": "REVIEW_FIRST",
        }