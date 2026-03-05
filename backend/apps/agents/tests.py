# apps/agents/tests.py
import pytest
from unittest.mock import MagicMock, patch


@pytest.mark.django_db
class TestTitleIntelligenceAgent:
    def _agent(self):
        from apps.agents.title_intelligence_agent import TitleIntelligenceAgent
        return TitleIntelligenceAgent.__new__(TitleIntelligenceAgent)

    def test_parse_valid_json(self):
        result = self._agent().parse_response(
            '{"trust_score": 85, "risk_level": "LOW", "flags": [], '
            '"summary_en": "Good", "summary_sw": "Nzuri", "recommendation": "BUY_SAFE"}'
        )
        assert result["trust_score"] == 85
        assert result["recommendation"] == "BUY_SAFE"

    def test_parse_code_fence(self):
        result = self._agent().parse_response(
            '```json\n{"trust_score": 60, "risk_level": "MEDIUM", "flags": [],'
            '"summary_en": "OK", "summary_sw": "Sawa", "recommendation": "REVIEW_FIRST"}\n```'
        )
        assert result["trust_score"] == 60

    def test_fallback_on_bad_json(self):
        result = self._agent().parse_response("NOT JSON AT ALL")
        assert result["trust_score"] == 50
        assert result["recommendation"] == "REVIEW_FIRST"

    def test_fallback_has_swahili(self):
        result = self._agent()._fallback_output()
        assert "summary_sw" in result
        assert len(result["summary_sw"]) > 0


@pytest.mark.django_db
class TestBuyerAssistantAgent:
    def test_chat_returns_reply(self, db):
        from apps.agents.buyer_assistant_agent import BuyerAssistantAgent
        mock_resp = MagicMock()
        mock_resp.content = [MagicMock(text="An LR Number is a Land Reference Number.")]
        with patch("apps.agents.buyer_assistant_agent.Anthropic") as MockAnth:
            MockAnth.return_value.messages.create.return_value = mock_resp
            result = BuyerAssistantAgent().chat("What is an LR Number?", "sess-1")
        assert "LR Number" in result["reply"]
        assert result["session_key"] == "sess-1"

    def test_history_persisted(self, db):
        from apps.agents.buyer_assistant_agent import BuyerAssistantAgent
        mock_resp = MagicMock()
        mock_resp.content = [MagicMock(text="Hello!")]
        with patch("apps.agents.buyer_assistant_agent.Anthropic") as MockAnth:
            MockAnth.return_value.messages.create.return_value = mock_resp
            agent = BuyerAssistantAgent()
            agent.chat("Hi", "persist-test")
            history = agent.get_history("persist-test")
        # user message + assistant reply = 2
        assert len(history) == 2

    def test_chat_with_property_context(self, db):
        from apps.agents.buyer_assistant_agent import BuyerAssistantAgent
        mock_resp = MagicMock()
        mock_resp.content = [MagicMock(text="This property looks good.")]
        ctx = {"title": "Test Plot", "county": "Nairobi", "trust_score": 75}
        with patch("apps.agents.buyer_assistant_agent.Anthropic") as MockAnth:
            MockAnth.return_value.messages.create.return_value = mock_resp
            result = BuyerAssistantAgent().chat("Tell me about this", "ctx-test",
                                                property_context=ctx)
        assert result["reply"] != ""


@pytest.mark.django_db
class TestAgentViews:
    def test_assistant_unauthenticated(self, api_client):
        r = api_client.post("/api/v1/agents/assistant/", {"message": "Hello"})
        assert r.status_code == 401

    def test_assistant_empty_message(self, buyer_client):
        r = buyer_client.post("/api/v1/agents/assistant/", {"message": ""})
        assert r.status_code == 400

    def test_assistant_message_too_long(self, buyer_client):
        r = buyer_client.post("/api/v1/agents/assistant/", {"message": "x" * 2001})
        assert r.status_code == 400

    def test_valuation_no_id(self, buyer_client):
        r = buyer_client.post("/api/v1/agents/valuation/", {})
        assert r.status_code == 400

    def test_valuation_unknown_property(self, buyer_client):
        r = buyer_client.post("/api/v1/agents/valuation/",
                              {"property_id": "00000000-0000-0000-0000-000000000000"})
        assert r.status_code == 404

    def test_valuation_stub_response(self, buyer_client, property_obj):
        r = buyer_client.post("/api/v1/agents/valuation/",
                              {"property_id": str(property_obj.id)})
        assert r.status_code == 200
        assert r.data["estimated_min_kes"] < r.data["estimated_max_kes"]