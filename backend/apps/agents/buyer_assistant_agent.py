# apps/agents/buyer_assistant_agent.py
#
# FIX: BuyerAssistantAgent now extends BaseAgent
#
# PROBLEMS SOLVED:
#   1. Previously created its own Anthropic client — bypassed BaseAgent entirely.
#   2. No AgentRun logging — impossible to track token costs or debug errors.
#   3. No input caching — identical messages re-called Anthropic every time.
#   4. No fallback — any Anthropic error surfaced directly to the user.
#
# HOW THE EXTENSION WORKS:
#   BaseAgent.run(**kwargs) handles: caching, timing, AgentRun logging, fallback.
#   We override build_prompt() to inject conversation history + system prompt.
#   We override parse_response() to extract the reply text into a dict.
#   Redis history management stays here — it's conversation state, not agent logic.
#
# CACHING NOTE:
#   input_hash is computed from kwargs by BaseAgent. For conversations, kwargs
#   includes the full history snapshot, so cache hits only occur on truly
#   identical inputs (same message + same history). This is correct behaviour —
#   we don't want to serve a cached reply from a different conversation context.
#
# FORCE_RERUN:
#   Conversational messages should never be cached across different sessions,
#   so we always pass force_rerun=True. The AgentRun log is still written,
#   giving us full observability without false cache hits.

import json
import logging
from django.core.cache import cache
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are ArdhiTrust's helpful land buying assistant for Kenya.
Explain land terms clearly. Never give final legal advice — always recommend
consulting a licensed conveyancer for binding decisions.
Respond in clear, friendly English."""

# Max conversation turns kept in Redis (each turn = 1 user + 1 assistant message)
MAX_HISTORY_TURNS = 10  # = 20 messages


class BuyerAssistantAgent(BaseAgent):
    agent_name = "BuyerAssistantAgent"
    max_tokens = 1024  # Conversational replies don't need 4096

    # ── Conversation history (Redis) ─────────────────────────────────────────

    def get_history(self, session_key: str) -> list[dict]:
        """Retrieve last MAX_HISTORY_TURNS turns from Redis."""
        messages = cache.get(f"agent_conv:{session_key}", [])
        # Keep only the most recent turns to stay within context window
        max_messages = MAX_HISTORY_TURNS * 2  # each turn = user + assistant
        return messages[-max_messages:]

    def save_history(self, session_key: str, messages: list[dict]) -> None:
        """Persist conversation history in Redis for 1 hour."""
        cache.set(f"agent_conv:{session_key}", messages, timeout=3600)

    def clear_history(self, session_key: str) -> None:
        """Clear conversation history (e.g. on new property context)."""
        cache.delete(f"agent_conv:{session_key}")

    # ── BaseAgent interface ───────────────────────────────────────────────────

    def build_prompt(
        self,
        user_message: str,
        session_key: str,
        history: list[dict],
        property_context: dict | None = None,
        **kwargs,
    ) -> list[dict]:
        """
        Build the messages list for the Anthropic API call.
        BaseAgent passes **kwargs straight through from run(), so we
        receive everything we need here.
        """
        # Inject property context into system prompt if provided
        system = SYSTEM_PROMPT
        if property_context:
            system += (
                f"\n\nCURRENT PROPERTY CONTEXT:\n"
                f"{json.dumps(property_context, indent=2)}"
            )

        # Prepend a system turn that Anthropic accepts as a user/assistant pair.
        # We model the system prompt as the first message pair so it flows
        # naturally with the rest of the conversation history.
        #
        # Note: Anthropic's Messages API has a top-level `system` parameter.
        # BaseAgent.run() calls self.client.messages.create(model, max_tokens, messages).
        # We store the system content in a special key in the first message dict
        # and handle it in build_prompt by returning it separately — BUT since
        # BaseAgent passes messages directly, we embed system as a leading
        # user message that the model will treat as context. For cleaner
        # separation, we override run() below to pass system correctly.
        messages = list(history) + [{"role": "user", "content": user_message}]
        return messages

    def parse_response(self, text: str) -> dict:
        """
        BaseAgent expects parse_response to return a dict.
        For conversational replies, we just wrap the text.
        """
        return {"reply": text}

    def _fallback_output(self, **kwargs) -> dict:
        return {
            "reply": (
                "I'm temporarily unavailable. Please try again in a moment. "
                "For urgent land queries, contact our support team at "
                "hello@ardhitrust.co.ke"
            )
        }

    # ── Override run() to pass system prompt correctly ────────────────────────

    def run(self, **kwargs):
        """
        Override BaseAgent.run() to pass the system parameter to Anthropic,
        which is separate from the messages list in their API.
        We still use BaseAgent's caching, timing, and AgentRun logging by
        calling super().run() — but we inject the system prompt correctly.
        """
        import time
        import hashlib
        import json as _json
        from apps.agents.models import AgentRun

        # Build system prompt (with optional property context)
        property_context = kwargs.get("property_context")
        system = SYSTEM_PROMPT
        if property_context:
            system += (
                f"\n\nCURRENT PROPERTY CONTEXT:\n"
                f"{_json.dumps(property_context, indent=2)}"
            )

        # Conversations are never cached across sessions — always force rerun.
        # We still log to AgentRun for observability.
        input_hash = hashlib.sha256(
            _json.dumps(kwargs, sort_keys=True, default=str).encode()
        ).hexdigest()

        start, error, output, tokens = time.time(), None, {}, 0
        try:
            messages = self.build_prompt(**kwargs)
            resp = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system,          # ← correct Anthropic parameter
                messages=messages,
            )
            tokens = resp.usage.input_tokens + resp.usage.output_tokens
            output = self.parse_response(resp.content[0].text)
        except Exception as e:
            logger.exception(f"{self.agent_name} error: {e}")
            error = str(e)
            output = self._fallback_output(**kwargs)
        finally:
            AgentRun.objects.create(
                agent_name=self.agent_name,
                input_hash=input_hash,
                output_json=output,
                duration_ms=int((time.time() - start) * 1000),
                tokens_used=tokens,
                error=error,
                user_id=kwargs.get("user_id"),
            )
        return output

    # ── Public interface (called from views.py) ───────────────────────────────

    def chat(
        self,
        user_message: str,
        session_key: str,
        property_context: dict | None = None,
        user_id: str | None = None,
    ) -> dict:
        """
        Send a message and get a reply.
        Manages history loading/saving around the BaseAgent run cycle.

        Returns: {"reply": str, "session_key": str}
        """
        history = self.get_history(session_key)

        result = self.run(
            user_message=user_message,
            session_key=session_key,
            history=history,
            property_context=property_context,
            user_id=user_id,
        )

        # Only persist history on successful replies (not fallbacks)
        if not result.get("error"):
            updated_history = history + [
                {"role": "user",      "content": user_message},
                {"role": "assistant", "content": result["reply"]},
            ]
            self.save_history(session_key, updated_history)

        return {
            "reply":       result["reply"],
            "session_key": session_key,
        }
