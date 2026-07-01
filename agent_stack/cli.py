"""Autonomous Agent Stack — CLI entry point.

Click-based command-line interface for multi-agent
orchestration and task delegation.
"""

from __future__ import annotations

import asyncio
import json

import click

from agent_stack import __version__
from agent_stack.core.orchestrator import AgentOrchestrator
from agent_stack.modules.security_agents import SecurityAgents
from agent_stack.modules.task_delegator import TaskDelegator


@click.group()
@click.version_option(version=__version__, prog_name="nexus-agent")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output.")
@click.pass_context
def main(ctx: click.Context, verbose: bool) -> None:
    """NEXUS Autonomous Agent Stack — Multi-agent orchestration.

    Task delegation, context isolation, and coordinated execution
    across cybersecurity domains.
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose


@main.command()
@click.option("--list", "-l", is_flag=True, help="List all available agents.")
def agents(list: bool) -> None:
    """Manage registered agents."""
    if list:
        for name in SecurityAgents.list():
            agent = SecurityAgents.get(name)
            if agent:
                click.echo(f"  {name:20s} {agent.description}")
    else:
        click.echo("Use --list to see available agents.")


@main.command()
@click.argument("goal")
@click.option("--agent", "-a", "agent_name", default=None, help="Agent to delegate to.")
@click.option("--target", "-t", default=None, help="Target for the task.")
def run(goal: str, agent_name: str | None, target: str | None) -> None:
    """Run a single task with automatic or manual agent delegation."""
    delegator = TaskDelegator()
    if agent_name:
        delegator.set_default(agent_name)

    task = delegator.delegate(goal, {"target": target} if target else {})
    click.echo(f"  Task: {task.name}")
    click.echo(f"  Agent: {task.agent_name}")
    click.echo(f"  Goal: {task.goal}")

    orchestrator = AgentOrchestrator()
    SecurityAgents.register_all(orchestrator)

    result = asyncio.run(orchestrator.execute(task))
    click.echo(f"  Status: {result.status.value}")
    if result.result:
        click.echo(f"  Result: {result.result}")


@main.command()
@click.argument("goals", nargs=-1, required=True)
@click.option("--parallel", "-p", is_flag=True, help="Execute in parallel (default: sequential).")
def batch(goals: tuple[str, ...], parallel: bool) -> None:
    """Run multiple tasks in parallel or sequentially."""
    delegator = TaskDelegator()
    tasks = delegator.delegate_batch(list(goals))

    orchestrator = AgentOrchestrator()
    SecurityAgents.register_all(orchestrator)

    if parallel:
        click.echo(f"  Executing {len(tasks)} tasks in parallel...")
        results = asyncio.run(orchestrator.execute_parallel(tasks))
    else:
        click.echo(f"  Executing {len(tasks)} tasks sequentially...")
        results = asyncio.run(orchestrator.execute_sequential(tasks))

    for task in results:
        status_icon = "✓" if task.status.value == "completed" else "✗"
        click.echo(f"  {status_icon} {task.id}: {task.status.value} ({task.name})")


@main.command()
@click.option("--json", "-j", "as_json", is_flag=True, help="Output as JSON.")
def status(as_json: bool) -> None:
    """Show orchestrator status and statistics."""
    orchestrator = AgentOrchestrator()
    SecurityAgents.register_all(orchestrator)
    summary = orchestrator.get_summary()

    if as_json:
        click.echo(json.dumps(summary, indent=2))
    else:
        click.echo(f"  Registered agents: {summary['registered_agents']}")
        click.echo(f"  Total tasks:       {summary['total_tasks']}")
        click.echo(f"  Completed:         {summary['completed']}")
        click.echo(f"  Failed:            {summary['failed']}")


if __name__ == "__main__":
    main()
