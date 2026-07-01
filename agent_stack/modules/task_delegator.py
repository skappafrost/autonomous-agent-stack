"""Task delegation engine — route tasks to appropriate agents.

Analyzes task goals and automatically assigns them to the most
appropriate registered agent based on domain expertise.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from agent_stack.core.orchestrator import Task


@dataclass
class DelegationRule:
    """Rule for task delegation.

    Attributes:
        pattern: Regex pattern to match task goals.
        agent_name: Agent to delegate to.
        priority: Rule priority (higher = evaluated first).
    """

    pattern: str
    agent_name: str
    priority: int = 0

    def matches(self, goal: str) -> bool:
        """Check if goal matches this rule."""
        return bool(re.search(self.pattern, goal, re.IGNORECASE))


class TaskDelegator:
    """Automatic task delegation based on goal analysis.

    Routes tasks to appropriate agents based on goal keywords
    and registered agent domains.

    Usage:
        delegator = TaskDelegator()
        delegator.add_rule(r"scan.*network|port.*scan", "network-scanner")
        delegator.add_rule(r"wifi|wireless|802.11", "wifi-auditor")

        task = delegator.delegate("Scan the WiFi network")
        result = await orchestrator.execute(task)
    """

    # Default delegation rules
    DEFAULT_RULES: list[tuple[str, str]] = [
        (r"scan.*network|port.*scan|discover.*host", "network-scanner"),
        (r"wifi|wireless|802\.11|ap.*scan", "wifi-auditor"),
        (r"web.*scan|recon.*web|endpoint.*discovery", "web-recon"),
    ]

    def __init__(self) -> None:
        """Initialize task delegator."""
        self._rules: list[DelegationRule] = []
        self._default_agent: Optional[str] = None
        self._setup_defaults()

    def _setup_defaults(self) -> None:
        """Set up default delegation rules."""
        for pattern, agent_name in self.DEFAULT_RULES:
            self._rules.append(DelegationRule(pattern=pattern, agent_name=agent_name))
        self._rules.sort(key=lambda r: r.priority, reverse=True)

    def add_rule(self, pattern: str, agent_name: str, priority: int = 0) -> None:
        """Add a custom delegation rule.

        Args:
            pattern: Regex pattern for goal matching.
            agent_name: Target agent name.
            priority: Rule priority (higher evaluated first).
        """
        self._rules.append(DelegationRule(pattern=pattern, agent_name=agent_name, priority=priority))
        self._rules.sort(key=lambda r: r.priority, reverse=True)

    def set_default(self, agent_name: str) -> None:
        """Set default agent for unmatched goals."""
        self._default_agent = agent_name

    def delegate(self, goal: str, context: Optional[dict] = None) -> Task:
        """Create a task delegated to the appropriate agent.

        Args:
            goal: Task description.
            context: Optional task context.

        Returns:
            Task with agent_name assigned.
        """
        agent_name = self._default_agent
        for rule in self._rules:
            if rule.matches(goal):
                agent_name = rule.agent_name
                break

        if not agent_name:
            agent_name = "default"

        return Task(name=self._infer_name(goal), goal=goal, agent_name=agent_name, context=context or {})

    def _infer_name(self, goal: str) -> str:
        """Infer a task name from the goal."""
        words = goal.lower().split()[:4]
        return "-".join(words) if words else "task"

    def delegate_batch(self, goals: list[str], context: Optional[dict] = None) -> list[Task]:
        """Create tasks for multiple goals."""
        return [self.delegate(goal, context) for goal in goals]
