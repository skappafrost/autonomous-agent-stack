"""Tests for core.orchestrator — AgentOrchestrator and Task."""

from __future__ import annotations

import pytest

from agent_stack.core.orchestrator import AgentOrchestrator, Task, TaskStatus


class TestTask:
    """Test Task dataclass."""

    def test_to_dict(self) -> None:
        """to_dict should return all fields."""
        task = Task(name="scan", goal="Scan network", agent_name="scanner")
        d = task.to_dict()
        assert d["name"] == "scan"
        assert d["status"] == "pending"
        assert d["agent_name"] == "scanner"

    def test_default_status(self) -> None:
        """Default status should be pending."""
        task = Task()
        assert task.status == TaskStatus.PENDING


class TestAgentOrchestrator:
    """Test orchestrator operations."""

    def test_register_and_list(self) -> None:
        """Should register and list agents."""
        orchestrator = AgentOrchestrator()

        class DummyAgent:
            async def execute(self, goal, context):
                return {"success": True}

        orchestrator.register("test-agent", DummyAgent())
        assert "test-agent" in orchestrator.list_agents()

    def test_unregister(self) -> None:
        """Should unregister agents."""
        orchestrator = AgentOrchestrator()

        class DummyAgent:
            async def execute(self, goal, context):
                return {}

        orchestrator.register("test-agent", DummyAgent())
        orchestrator.unregister("test-agent")
        assert "test-agent" not in orchestrator.list_agents()

    def test_get_summary_empty(self) -> None:
        """Should return empty summary."""
        orchestrator = AgentOrchestrator()
        summary = orchestrator.get_summary()
        assert summary["registered_agents"] == 0
        assert summary["total_tasks"] == 0

    @pytest.mark.asyncio
    async def test_execute_missing_agent(self) -> None:
        """Should fail if agent not registered."""
        orchestrator = AgentOrchestrator()
        task = Task(name="test", goal="Test", agent_name="missing")
        result = await orchestrator.execute(task)
        assert result.status == TaskStatus.FAILED
        assert "not registered" in (result.error or "")

    @pytest.mark.asyncio
    async def test_execute_parallel(self) -> None:
        """Should execute tasks in parallel."""
        orchestrator = AgentOrchestrator()

        class FastAgent:
            async def execute(self, goal, context):
                return {"done": True}

        orchestrator.register("fast", FastAgent())
        tasks = [
            Task(name=f"task-{i}", goal=f"Goal {i}", agent_name="fast")
            for i in range(3)
        ]
        results = await orchestrator.execute_parallel(tasks)
        assert len(results) == 3
