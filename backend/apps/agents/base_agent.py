# apps/agents/base_agent.py
import time, hashlib, json, logging
from abc import ABC, abstractmethod
from anthropic import Anthropic
from django.conf import settings

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    agent_name: str = "BaseAgent"
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 4096

    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    @abstractmethod
    def build_prompt(self, **kwargs) -> list[dict]: ...

    @abstractmethod
    def parse_response(self, text: str) -> dict: ...

    def run(self, **kwargs) -> dict:
        from apps.agents.models import AgentRun

        input_hash = hashlib.sha256(
            json.dumps(kwargs, sort_keys=True, default=str).encode()
        ).hexdigest()

        # Cache hit — skip re-running identical inputs
        cached = AgentRun.objects.filter(
            agent_name=self.agent_name, input_hash=input_hash, error=None
        ).order_by("-created_at").first()
        if cached and not kwargs.get("force_rerun"):
            return cached.output_json

        start, error, output, tokens = time.time(), None, {}, 0
        try:
            messages = self.build_prompt(**kwargs)
            resp     = self.client.messages.create(
                model=self.model, max_tokens=self.max_tokens, messages=messages
            )
            tokens = resp.usage.input_tokens + resp.usage.output_tokens
            output = self.parse_response(resp.content[0].text)
        except Exception as e:
            logger.exception(f"{self.agent_name} error: {e}")
            error  = str(e)
            output = self._fallback_output(**kwargs)
        finally:
            AgentRun.objects.create(
                agent_name=self.agent_name,
                input_hash=input_hash,
                output_json=output,
                duration_ms=int((time.time() - start) * 1000),
                tokens_used=tokens,
                error=error,
                property_id=kwargs.get("property_id"),
                user_id=kwargs.get("user_id"),
            )
        return output

    def _fallback_output(self, **kwargs) -> dict:
        return {"error": True, "message": "Agent temporarily unavailable."}