"""Autonomous Agent Stack — Multi-agent orchestration framework.

Task delegation, context isolation, and coordinated execution across
cybersecurity domains.
"""

__version__ = "1.0.0"
__author__ = "NEXUS"

from agent_stack.core.orchestrator import AgentOrchestrator
from agent_stack.core.agent import BaseAgent
from agent_stack.core.context import ContextManager

__all__ = ["AgentOrchestrator", "BaseAgent", "ContextManager"]
