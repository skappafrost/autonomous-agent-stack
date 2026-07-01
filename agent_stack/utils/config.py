"""Agent stack configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AgentConfig:
    """Global configuration for the Agent Stack."""

    max_concurrent: int = 5
    timeout: int = 300
    log_level: str = "INFO"
    verbose: bool = False
    persist_dir: Path = Path(".agent-context")

    @classmethod
    def from_env(cls) -> AgentConfig:
        """Load configuration from environment."""
        return cls(
            max_concurrent=int(os.getenv("AGENT_MAX_CONCURRENT", "5")),
            timeout=int(os.getenv("AGENT_TIMEOUT", "300")),
            verbose=os.getenv("AGENT_VERBOSE", "").lower() in ("1", "true", "yes"),
        )

    def ensure_dirs(self) -> None:
        """Create necessary directories."""
        self.persist_dir.mkdir(parents=True, exist_ok=True)
