# Autonomous Agent Stack

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Beta-orange)
![Multi-Agent](https://img.shields.io/badge/Type-Multi--Agent-purple)

**Multi-agent orchestration framework** for parallel security operations. Task delegation, context isolation, and coordinated execution across cybersecurity domains.

Built by [NEXUS](https://skappafrost.github.io/nexus-website/) — an autonomous cybersecurity intelligence system.

---

## ⚠️ Legal Disclaimer

This tool is designed for **authorized security assessment and research**. Ensure compliance with applicable laws and obtain proper authorization before scanning or testing any systems. By using this software, you agree that:

1. You will only use this tool on systems you own or have explicit authorization to test.
2. You accept full responsibility for any actions performed using this framework.
3. The authors bear **no liability** for misuse or unauthorized testing.
4. Unauthorized access to computer systems is illegal in most jurisdictions.
5. Always follow responsible disclosure practices when vulnerabilities are found.

---

## Features

| # | Module | Description |
|---|--------|-------------|
| 1 | **AgentOrchestrator** | Multi-agent pool, task delegation, parallel/sequential execution |
| 2 | **BaseAgent** | Abstract agent interface with lifecycle hooks (initialize → execute → cleanup) |
| 3 | **ContextManager** | Isolated state management per agent/task, shared state for coordination |
| 4 | **SecurityAgent** | Concrete base for security-focused agents with domain configuration |
| 5 | **SecurityAgents** | Pre-built factory: network-scanner, web-recon, wifi-auditor |
| 6 | **TaskDelegator** | Automatic goal-to-agent routing with regex pattern matching |
| 7 | **AgentResult** | Structured result with success, data, error, duration, metadata |
| 8 | **TaskStatus** | Full lifecycle: pending → running → completed/failed/cancelled |
| 9 | **AgentConfig** | Environment-based configuration with sensible defaults |
| 10 | **CLI** | Click-based: `nexus-agent run`, `batch`, `agents`, `status` |
| 11 | **AsyncIO** | Full async support with semaphore-bounded concurrency |
| 12 | **Persistence** | Context save/load for cross-session state management |

---

## Installation

```bash
git clone https://github.com/skappafrost/autonomous-agent-stack.git
cd autonomous-agent-stack
pip install -e .

# With dev dependencies
pip install -e ".[dev]"
```

### Prerequisites

- **Python 3.11+**
- **Pydantic 2.0+** (data validation)
- **Rich 13.0+** (terminal formatting)
- **httpx 0.27+** (async HTTP client)

---

## Quick Start

### Python API

```python
import asyncio
from agent_stack.core.orchestrator import AgentOrchestrator, Task
from agent_stack.modules.security_agents import SecurityAgents

# Initialize orchestrator
orchestrator = AgentOrchestrator(max_concurrent=3)
SecurityAgents.register_all(orchestrator)

# Create and execute tasks
task1 = Task(name="scan", goal="Scan network for hosts", agent_name="network-scanner")
task2 = Task(name="wifi", goal="Audit WiFi networks", agent_name="wifi-auditor")

# Run in parallel
results = asyncio.run(orchestrator.execute_parallel([task1, task2]))
for r in results:
    print(f"{r.id}: {r.status.value}")
```

### CLI Usage

```bash
# List available agents
nexus-agent agents --list

# Run a single task
nexus-agent run "Scan the network" --target 192.168.1.0/24

# Run multiple tasks in parallel
nexus-agent batch "Scan network" "Audit WiFi" --parallel

# Check orchestrator status
nexus-agent status
```

---

## Architecture

```
agent_stack/
├── __init__.py          # Package metadata
├── __main__.py          # python -m agent_stack entry
├── cli.py               # Click CLI (run, batch, agents, status)
├── core/
│   ├── orchestrator.py  # AgentOrchestrator — task dispatch & lifecycle
│   ├── agent.py         # BaseAgent, SecurityAgent, AgentResult
│   └── context.py       # ContextManager — scoped state isolation
├── modules/
│   ├── security_agents.py  # Pre-built agent factory
│   └── task_delegator.py   # Automatic goal-to-agent routing
└── utils/
    ├── config.py        # AgentConfig — env-based settings
    └── logger.py        # Structured logging
```

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `AGENT_MAX_CONCURRENT` | `5` | Maximum parallel tasks |
| `AGENT_TIMEOUT` | `300` | Task timeout in seconds |
| `AGENT_VERBOSE` | `false` | Verbose output mode |

---

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check agent_stack/ tests/
mypy agent_stack/ --ignore-missing-imports
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

⭐ **Star this repo** if you find it useful. For questions or collaboration, reach out via [GitHub](https://github.com/skappafrost).
