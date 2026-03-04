# apps/agents/buyer_assistant_agent.py
import json
from django.core.cache import cache
from anthropic import Anthropic
from django.conf import settings

SYSTEM = """You are ArdhiTrust's helpful land buying assistant for Kenya.
Explain land terms clearly. Never give final legal advice — always recommend 
consulting a licensed conveyancer for binding decisions.
Respond in clear, friendly English."""

class BuyerAssistantAgent:
    model = "claude-sonnet-4-20250514"

    def get_history(self, session_key: str) -> list[dict]:
        return cache.get(f"agent_conv:{session_key}", [])[-20:]

    def save_history(self, session_key: str, messages: list[dict]):
        cache.set(f"agent_conv:{session_key}", messages, timeout=3600)

    def chat(self, user_message: str, session_key: str, property_context: dict = None) -> dict:
        history = self.get_history(session_key)
        messages = history + [{"role": "user", "content": user_message}]

        system = SYSTEM
        if property_context:
            system += f"\n\nCURRENT PROPERTY:\n{json.dumps(property_context, indent=2)}"

        client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        resp = client.messages.create(
            model=self.model, max_tokens=1024,
            system=system, messages=messages,
        )

        reply = resp.content[0].text
        messages.append({"role": "assistant", "content": reply})
        self.save_history(session_key, messages)

        return {"reply": reply, "session_key": session_key}