"""Tests for core.agent — BaseAgent, SecurityAgent, AgentResult."""

from __future__ import annotations

import pytest

from agent_stack.core.agent import AgentResult, SecurityAgent


class TestAgentResult:
    """Test AgentResult dataclass."""

    def test_to_dict(self) -> None:
        """to_dict should return all fields."""
        result = AgentResult(success=True, data={"found": 5})
        d = result.to_dict()
        assert d["success"] is True

    def test_default_values(self) -> None:
        """Default values should be set."""
        result = AgentResult()
        assert result.success is True
        assert result.data is None
        assert result.error is None
        assert result.duration == 0.0


class TestSecurityAgent:
    """Test SecurityAgent base class."""

    @pytest.mark.asyncio
    async def test_execute_returns_result(self) -> None:
        """Should return AgentResult."""
        agent = SecurityAgent(name="test-agent", domain="test")
        result = await agent.execute("test goal", {"target": "127.0.0.1"})
        assert isinstance(result, AgentResult)
        assert result.success is True
        assert result.metadata["domain"] == "test"

    def test_get_info(self) -> None:
        """Should return agent info."""
        agent = SecurityAgent(name="test-agent", domain="test")
        info = agent.get_info()
        assert info["name"] == "test-agent"
        assert info["state"] == "idle"

    def test_execution_count_initial(self) -> None:
        """Initial execution count should be zero."""
        agent = SecurityAgent(name="test-agent", domain="test")
        assert agent.execution_count == 0

    def test_last_result_initial(self) -> None:
        """Initial last_result should be None."""
        agent = SecurityAgent(name="test-agent", domain="test")
        assert agent.last_result is None
