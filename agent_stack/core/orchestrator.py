"""Agent orchestrator — multi-agent task delegation and lifecycle management.

Manages a pool of agents, dispatches tasks, monitors progress,
and aggregates results from parallel execution.
"""

from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from agent_stack.core.agent import BaseAgent
from agent_stack.core.context import ContextManager


class TaskStatus(str, Enum):
    """Status of a delegated task."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """A task to be delegated to an agent.

    Attributes:
        id: Unique task identifier.
        name: Human-readable task name.
        goal: Task description/goal.
        context: Additional context for the agent.
        agent_name: Name of the agent to handle this task.
        status: Current task status.
        result: Task result (populated on completion).
        error: Error message (populated on failure).
        created_at: Task creation timestamp.
        completed_at: Task completion timestamp.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    goal: str = ""
    context: dict = field(default_factory=dict)
    agent_name: str = ""
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "goal": self.goal,
            "agent_name": self.agent_name,
            "status": self.status.value,
            "result": str(self.result)[:200] if self.result else None,
            "error": self.error,
            "duration": round(self.completed_at - self.created_at, 2) if self.completed_at else None,
        }


class AgentOrchestrator:
    """Orchestrate multi-agent task execution.

    Manages agent registration, task delegation, parallel execution,
    and result aggregation for coordinated security operations.

    Usage:
        orchestrator = AgentOrchestrator()
        orchestrator.register("scanner", ScannerAgent())
        orchestrator.register("analyzer", AnalyzerAgent())

        task1 = Task(name="scan", goal="Scan network", agent_name="scanner")
        task2 = Task(name="analyze", goal="Analyze results", agent_name="analyzer")

        results = await orchestrator.execute_parallel([task1, task2])
    """

    def __init__(self, max_concurrent: int = 5, timeout: int = 300) -> None:
        """Initialize orchestrator.

        Args:
            max_concurrent: Maximum number of concurrent tasks.
            timeout: Task execution timeout in seconds.
        """
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        self._agents: dict[str, BaseAgent] = {}
        self._tasks: dict[str, Task] = {}
        self._context = ContextManager()

    def register(self, name: str, agent: BaseAgent) -> None:
        """Register an agent for task delegation.

        Args:
            name: Agent name (used in Task.agent_name).
            agent: Agent instance.
        """
        self._agents[name] = agent

    def unregister(self, name: str) -> None:
        """Unregister an agent.

        Args:
            name: Agent name to remove.
        """
        self._agents.pop(name, None)

    def list_agents(self) -> list[str]:
        """List all registered agent names."""
        return sorted(self._agents.keys())

    async def execute(self, task: Task) -> Task:
        """Execute a single task.

        Args:
            task: Task to execute.

        Returns:
            Updated Task with result or error.
        """
        if task.agent_name not in self._agents:
            task.status = TaskStatus.FAILED
            task.error = f"Agent '{task.agent_name}' not registered"
            task.completed_at = time.time()
            return task

        agent = self._agents[task.agent_name]
        task.status = TaskStatus.RUNNING
        self._tasks[task.id] = task

        try:
            result = await asyncio.wait_for(
                agent.execute(task.goal, task.context),
                timeout=self.timeout,
            )
            task.result = result
            task.status = TaskStatus.COMPLETED
        except asyncio.TimeoutError:
            task.status = TaskStatus.FAILED
            task.error = f"Task timed out after {self.timeout}s"
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
        finally:
            task.completed_at = time.time()

        return task

    async def execute_parallel(self, tasks: list[Task]) -> list[Task]:
        """Execute multiple tasks in parallel.

        Respects max_concurrent limit using a semaphore.

        Args:
            tasks: List of tasks to execute.

        Returns:
            List of completed tasks.
        """
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def _run_with_semaphore(task: Task) -> Task:
            async with semaphore:
                return await self.execute(task)

        results = await asyncio.gather(*[_run_with_semaphore(t) for t in tasks])
        return list(results)

    async def execute_sequential(self, tasks: list[Task]) -> list[Task]:
        """Execute tasks sequentially (each waits for previous).

        Args:
            tasks: List of tasks in execution order.

        Returns:
            List of completed tasks.
        """
        results: list[Task] = []
        for task in tasks:
            result = await self.execute(task)
            results.append(result)
            if result.status == TaskStatus.FAILED:
                break
        return results

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        return self._tasks.get(task_id)

    def get_all_tasks(self) -> list[Task]:
        """Get all tasks."""
        return list(self._tasks.values())

    def get_summary(self) -> dict:
        """Get orchestrator summary statistics."""
        tasks = list(self._tasks.values())
        return {
            "registered_agents": len(self._agents),
            "total_tasks": len(tasks),
            "completed": sum(1 for t in tasks if t.status == TaskStatus.COMPLETED),
            "failed": sum(1 for t in tasks if t.status == TaskStatus.FAILED),
            "running": sum(1 for t in tasks if t.status == TaskStatus.RUNNING),
            "pending": sum(1 for t in tasks if t.status == TaskStatus.PENDING),
        }
