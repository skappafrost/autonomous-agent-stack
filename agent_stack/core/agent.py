"""Base agent — abstract agent interface with lifecycle hooks.

Defines the contract for all agents in the stack, including
initialization, execution, and cleanup lifecycle phases.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from agent_stack.core.context import ContextManager


class AgentState(str, Enum):
    """Agent lifecycle state."""

    IDLE = "idle"
    INITIALIZING = "initializing"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"


@dataclass
class AgentResult:
    """Result from an agent execution.

    Attributes:
        success: Whether the execution succeeded.
        data: Result data payload.
        error: Error message if failed.
        duration: Execution duration in seconds.
        metadata: Additional metadata.
    """

    success: bool = True
    data: Any = None
    error: Optional[str] = None
    duration: float = 0.0
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "data": str(self.data)[:200] if self.data else None,
            "error": self.error,
            "duration": self.duration,
            "metadata": self.metadata,
        }


class BaseAgent(ABC):
    """Abstract base class for all agents in the stack.

    Provides lifecycle hooks (initialize, execute, cleanup) and
    context management for isolated agent execution.

    Subclasses must implement the `execute` method with their
    specific task logic.

    Usage:
        class ScannerAgent(BaseAgent):
            async def execute(self, goal: str, context: dict) -> AgentResult:
                # ... scanning logic ...
                return AgentResult(success=True, data={"found": 5})
    """

    def __init__(self, name: str, description: str = "") -> None:
        """Initialize base agent.

        Args:
            name: Agent identifier.
            description: Human-readable description.
        """
        self.name = name
        self.description = description
        self.state = AgentState.IDLE
        self._context = ContextManager()
        self._execution_count = 0
        self._last_result: Optional[AgentResult] = None

    @abstractmethod
    async def execute(self, goal: str, context: dict) -> AgentResult:
        """Execute the agent's primary task.

        Args:
            goal: Task description/goal.
            context: Additional context for execution.

        Returns:
            AgentResult with execution outcome.
        """
        ...

    async def initialize(self) -> None:
        """Initialize the agent before first execution.

        Override to set up resources, connections, or state.
        """
        self.state = AgentState.INITIALIZING
        # Subclass-specific initialization
        self.state = AgentState.IDLE

    async def cleanup(self) -> None:
        """Clean up resources after execution.

        Override to release resources, close connections, etc.
        """
        self.state = AgentState.STOPPED

    async def run(self, goal: str, context: Optional[dict] = None) -> AgentResult:
        """Full execution lifecycle: initialize → execute → cleanup.

        Args:
            goal: Task description/goal.
            context: Additional context.

        Returns:
            AgentResult with execution outcome.
        """
        start_time = time.time()
        self.state = AgentState.RUNNING

        try:
            await self.initialize()
            result = await self.execute(goal, context or {})
            result.duration = time.time() - start_time
            self._last_result = result
            self._execution_count += 1

            if result.success:
                self.state = AgentState.COMPLETED
            else:
                self.state = AgentState.FAILED

            return result
        except Exception as e:
            self.state = AgentState.FAILED
            return AgentResult(
                success=False,
                error=str(e),
                duration=time.time() - start_time,
            )
        finally:
            await self.cleanup()

    @property
    def execution_count(self) -> int:
        """Number of times this agent has been executed."""
        return self._execution_count

    @property
    def last_result(self) -> Optional[AgentResult]:
        """Result from the last execution."""
        return self._last_result

    def get_info(self) -> dict:
        """Get agent information."""
        return {
            "name": self.name,
            "description": self.description,
            "state": self.state.value,
            "execution_count": self._execution_count,
        }


class SecurityAgent(BaseAgent):
    """Concrete agent for security assessment tasks.

    Provides a base implementation for security-focused agents
    with configurable domain and tool access.
    """

    def __init__(
        self,
        name: str = "security-agent",
        domain: str = "general",
        tools: Optional[list[str]] = None,
    ) -> None:
        """Initialize security agent.

        Args:
            name: Agent identifier.
            domain: Security domain (network, web, wireless, etc.).
            tools: Available tool names.
        """
        super().__init__(name=name, description=f"Security agent for {domain} domain")
        self.domain = domain
        self.tools = tools or []

    async def execute(self, goal: str, context: dict) -> AgentResult:
        """Execute a security assessment task.

        Args:
            goal: Assessment goal description.
            context: Target and configuration context.

        Returns:
            AgentResult with assessment findings.
        """
        # Base implementation — subclasses override with specific logic
        return AgentResult(
            success=True,
            data={
                "domain": self.domain,
                "goal": goal,
                "tools_available": self.tools,
                "target": context.get("target", "unknown"),
                "findings": [],
            },
            metadata={"agent": self.name, "domain": self.domain},
        )
