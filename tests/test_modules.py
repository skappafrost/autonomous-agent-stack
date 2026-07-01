"""Tests for modules — SecurityAgents and TaskDelegator."""

from __future__ import annotations

import pytest

from agent_stack.modules.security_agents import SecurityAgents
from agent_stack.modules.task_delegator import TaskDelegator


class TestSecurityAgents:
    """Test security agents factory."""

    def test_list(self) -> None:
        """Should list available agents."""
        names = SecurityAgents.list()
        assert "network-scanner" in names
        assert "web-recon" in names
        assert "wifi-auditor" in names

    def test_get_existing(self) -> None:
        """Should return agent instance."""
        agent = SecurityAgents.get("network-scanner")
        assert agent is not None
        assert agent.name == "network-scanner"

    def test_get_missing(self) -> None:
        """Should return None for missing agent."""
        agent = SecurityAgents.get("nonexistent")
        assert agent is None

    @pytest.mark.asyncio
    async def test_network_scanner_execute(self) -> None:
        """Network scanner should return scan results."""
        agent = SecurityAgents.get("network-scanner")
        assert agent is not None
        result = await agent.execute("scan", {"target": "192.168.1.0/24"})
        assert result.success is True
        assert "ports" in result.data

    @pytest.mark.asyncio
    async def test_wifi_auditor_execute(self) -> None:
        """WiFi auditor should return audit results."""
        agent = SecurityAgents.get("wifi-auditor")
        assert agent is not None
        result = await agent.execute("audit", {"target": "wlan0"})
        assert result.success is True
        assert "aps" in result.data


class TestTaskDelegator:
    """Test task delegation."""

    def test_delegate_network(self) -> None:
        """Should delegate network tasks."""
        delegator = TaskDelegator()
        task = delegator.delegate("Scan the network for hosts")
        assert task.agent_name == "network-scanner"

    def test_delegate_wifi(self) -> None:
        """Should delegate WiFi tasks."""
        delegator = TaskDelegator()
        task = delegator.delegate("Audit WiFi networks")
        assert task.agent_name == "wifi-auditor"

    def test_delegate_web(self) -> None:
        """Should delegate web tasks."""
        delegator = TaskDelegator()
        task = delegator.delegate("Perform web reconnaissance on target")
        assert task.agent_name == "web-recon"

    def test_custom_rule(self) -> None:
        """Should apply custom rules."""
        delegator = TaskDelegator()
        delegator.add_rule(r"custom.*task", "network-scanner", priority=10)
        task = delegator.delegate("Run custom task now")
        assert task.agent_name == "network-scanner"

    def test_default_agent(self) -> None:
        """Should use default for unmatched goals."""
        delegator = TaskDelegator()
        delegator.set_default("web-recon")
        task = delegator.delegate("Do something completely unknown")
        assert task.agent_name == "web-recon"

    def test_delegate_batch(self) -> None:
        """Should delegate multiple goals."""
        delegator = TaskDelegator()
        tasks = delegator.delegate_batch(["Scan network", "Audit WiFi"])
        assert len(tasks) == 2
        assert tasks[0].agent_name == "network-scanner"
        assert tasks[1].agent_name == "wifi-auditor"

    def test_infer_name(self) -> None:
        """Should infer task name from goal."""
        delegator = TaskDelegator()
        task = delegator.delegate("Scan the network")
        assert len(task.name) > 0
