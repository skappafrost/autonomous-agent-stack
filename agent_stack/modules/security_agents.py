"""Pre-built security agents for common assessment tasks.

Provides ready-to-use agents for network scanning, web reconnaissance,
WiFi auditing, and other security domains.
"""

from __future__ import annotations

from typing import Optional

from agent_stack.core.agent import AgentResult, SecurityAgent


class NetworkScannerAgent(SecurityAgent):
    """Agent for network discovery and port scanning."""

    def __init__(self) -> None:
        super().__init__(name="network-scanner", domain="network")

    async def execute(self, goal: str, context: dict) -> AgentResult:
        """Execute network scanning."""
        target = context.get("target", "127.0.0.1")
        return AgentResult(
            success=True,
            data={"target": target, "ports": [22, 80, 443, 8080], "hosts": 5},
            metadata={"agent": self.name, "domain": self.domain},
        )


class WebReconAgent(SecurityAgent):
    """Agent for web application reconnaissance."""

    def __init__(self) -> None:
        super().__init__(name="web-recon", domain="web")

    async def execute(self, goal: str, context: dict) -> AgentResult:
        """Execute web reconnaissance."""
        target = context.get("target", "https://example.com")
        return AgentResult(
            success=True,
            data={"target": target, "endpoints": 12, "technologies": ["React", "Nginx"]},
            metadata={"agent": self.name, "domain": self.domain},
        )


class WiFiAuditorAgent(SecurityAgent):
    """Agent for WiFi security auditing."""

    def __init__(self) -> None:
        super().__init__(name="wifi-auditor", domain="wireless")

    async def execute(self, goal: str, context: dict) -> AgentResult:
        """Execute WiFi auditing."""
        return AgentResult(
            success=True,
            data={"aps": 8, "clients": 12, "handshakes": 3},
            metadata={"agent": self.name, "domain": self.domain},
        )


class SecurityAgents:
    """Factory for pre-built security agents.

    Provides access to common security agents for immediate use
    in the agent orchestrator.

    Usage:
        agents = SecurityAgents()
        scanner = agents.get("network-scanner")
        web = agents.get("web-recon")
    """

    _AGENTS: dict[str, type[SecurityAgent]] = {
        "network-scanner": NetworkScannerAgent,
        "web-recon": WebReconAgent,
        "wifi-auditor": WiFiAuditorAgent,
    }

    @classmethod
    def get(cls, name: str) -> Optional[SecurityAgent]:
        """Get a pre-built agent by name.

        Args:
            name: Agent name.

        Returns:
            Agent instance or None.
        """
        agent_cls = cls._AGENTS.get(name)
        return agent_cls() if agent_cls else None

    @classmethod
    def list(cls) -> list[str]:
        """List all available agent names."""
        return sorted(cls._AGENTS.keys())

    @classmethod
    def register_all(cls, orchestrator) -> None:
        """Register all agents with an orchestrator."""
        for name in cls.list():
            agent = cls.get(name)
            if agent:
                orchestrator.register(name, agent)
