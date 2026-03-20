# apps/agents/tests.py  (BuyerAssistantAgent section — replaces existing tests)

import pytest
from unittest.mock import MagicMock, patch


@pytest.mark.django_db
class TestBuyerAssistantAgent:

    def _mock_response(self, text: str):
        mock_resp = MagicMock()
        mock_resp.content = [MagicMock(text=text)]
        mock_resp.usage.input_tokens = 50
        mock_resp.usage.output_tokens = 30
        return mock_resp

    def _make_agent(self):
        from apps.agents.buyer_assistant_agent import BuyerAssistantAgent
        agent = BuyerAssistantAgent()
        return agent

    # ── build_prompt ─────────────────────────────────────────────────────────

    def test_build_prompt_no_history(self, db):
        agent = self._make_agent()
        messages = agent.build_prompt(
            user_message="What is an LR Number?",
            session_key="sess-1",
            history=[],
        )
        assert messages[-1] == {"role": "user", "content": "What is an LR Number?"}
        assert len(messages) == 1

    def test_build_prompt_with_history(self, db):
        agent = self._make_agent()
        history = [
            {"role": "user",      "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]
        messages = agent.build_prompt(
            user_message="Tell me more",
            session_key="sess-2",
            history=history,
        )
        assert len(messages) == 3
        assert messages[-1]["content"] == "Tell me more"

    # ── parse_response ────────────────────────────────────────────────────────

    def test_parse_response_returns_dict(self, db):
        agent = self._make_agent()
        result = agent.parse_response("An LR Number is a Land Reference Number.")
        assert isinstance(result, dict)
        assert result["reply"] == "An LR Number is a Land Reference Number."

    # ── fallback ──────────────────────────────────────────────────────────────

    def test_fallback_output_has_reply(self, db):
        agent = self._make_agent()
        result = agent._fallback_output()
        assert "reply" in result
        assert len(result["reply"]) > 0

    def test_fallback_output_is_helpful(self, db):
        agent = self._make_agent()
        result = agent._fallback_output()
        # Should mention a way to get help, not just an error
        assert "ardhitrust" in result["reply"].lower() or "support" in result["reply"].lower()

    # ── chat (integration) ────────────────────────────────────────────────────

    def test_chat_returns_reply_and_session_key(self, db):
        agent = self._make_agent()
        with patch.object(agent, "client") as mock_client:
            mock_client.messages.create.return_value = self._mock_response(
                "An LR Number is a Land Reference Number."
            )
            result = agent.chat("What is an LR Number?", session_key="sess-1")

        assert "reply" in result
        assert result["session_key"] == "sess-1"
        assert "LR Number" in result["reply"]

    def test_chat_persists_history(self, db):
        agent = self._make_agent()
        with patch.object(agent, "client") as mock_client:
            mock_client.messages.create.return_value = self._mock_response("Hello!")
            agent.chat("Hi", session_key="persist-test")

        history = agent.get_history("persist-test")
        # user message + assistant reply = 2
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "assistant"

    def test_chat_with_property_context(self, db):
        agent = self._make_agent()
        ctx = {"title": "Test Plot", "county": "Nairobi", "trust_score": 75}
        with patch.object(agent, "client") as mock_client:
            mock_client.messages.create.return_value = self._mock_response(
                "This property looks good."
            )
            result = agent.chat(
                "Tell me about this property",
                session_key="ctx-test",
                property_context=ctx,
            )

        assert result["reply"] != ""
        # Verify property context was injected into the system prompt
        call_kwargs = mock_client.messages.create.call_args[1]
        assert "system" in call_kwargs
        assert "Nairobi" in call_kwargs["system"]

    def test_chat_history_grows_across_turns(self, db):
        agent = self._make_agent()
        with patch.object(agent, "client") as mock_client:
            mock_client.messages.create.return_value = self._mock_response("Reply 1")
            agent.chat("Message 1", session_key="multi-turn")

            mock_client.messages.create.return_value = self._mock_response("Reply 2")
            agent.chat("Message 2", session_key="multi-turn")

        history = agent.get_history("multi-turn")
        assert len(history) == 4  # 2 turns × (user + assistant)

    def test_chat_second_turn_sends_history(self, db):
        """Second message must include prior history in the API call."""
        agent = self._make_agent()
        with patch.object(agent, "client") as mock_client:
            mock_client.messages.create.return_value = self._mock_response("Reply 1")
            agent.chat("First message", session_key="history-check")

            mock_client.messages.create.return_value = self._mock_response("Reply 2")
            agent.chat("Second message", session_key="history-check")

            # Second call should have 3 messages: prior user+assistant + new user
            second_call_messages = mock_client.messages.create.call_args[1]["messages"]
            assert len(second_call_messages) == 3

    def test_fallback_does_not_corrupt_history(self, db):
        """If the API fails, history should not be updated."""
        agent = self._make_agent()
        with patch.object(agent, "client") as mock_client:
            mock_client.messages.create.side_effect = Exception("API error")
            result = agent.chat("This will fail", session_key="fail-test")

        # Fallback reply returned
        assert "reply" in result
        # History should be empty — we don't save on failure
        history = agent.get_history("fail-test")
        assert len(history) == 0

    def test_agent_run_logged(self, db):
        """Every chat call should create an AgentRun record."""
        from apps.agents.models import AgentRun
        agent = self._make_agent()
        with patch.object(agent, "client") as mock_client:
            mock_client.messages.create.return_value = self._mock_response("Hello!")
            agent.chat("Hi", session_key="log-test")

        run = AgentRun.objects.filter(agent_name="BuyerAssistantAgent").first()
        assert run is not None
        assert run.tokens_used == 80  # 50 input + 30 output

    def test_agent_run_logged_on_error(self, db):
        """Even failed calls should log an AgentRun with error field set."""
        from apps.agents.models import AgentRun
        agent = self._make_agent()
        with patch.object(agent, "client") as mock_client:
            mock_client.messages.create.side_effect = Exception("Network error")
            agent.chat("Hi", session_key="error-log-test")

        run = AgentRun.objects.filter(agent_name="BuyerAssistantAgent").first()
        assert run is not None
        assert run.error is not None
        assert "Network error" in run.error

    def test_clear_history(self, db):
        agent = self._make_agent()
        with patch.object(agent, "client") as mock_client:
            mock_client.messages.create.return_value = self._mock_response("Hi!")
            agent.chat("Hello", session_key="clear-test")

        agent.clear_history("clear-test")
        assert agent.get_history("clear-test") == []

    def test_history_truncated_to_max_turns(self, db):
        """History should not grow beyond MAX_HISTORY_TURNS * 2 messages."""
        from apps.agents.buyer_assistant_agent import MAX_HISTORY_TURNS
        agent = self._make_agent()

        # Manually stuff history beyond the limit
        long_history = []
        for i in range(MAX_HISTORY_TURNS + 5):
            long_history.append({"role": "user",      "content": f"msg {i}"})
            long_history.append({"role": "assistant",  "content": f"reply {i}"})
        agent.save_history("trim-test", long_history)

        retrieved = agent.get_history("trim-test")
        assert len(retrieved) <= MAX_HISTORY_TURNS * 2
