"""Context manager — isolated state management per agent and task.

Provides context isolation between agents, shared state for
coordination, and data passing between sequential tasks.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


@dataclass
class ContextEntry:
    """A single context entry.

    Attributes:
        key: Context key.
        value: Context value.
        scope: Scope (agent, task, shared).
        owner: Owner identifier (agent name or task ID).
        timestamp: When the entry was created.
    """

    key: str
    value: Any
    scope: str = "shared"
    owner: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "key": self.key,
            "value": self.value,
            "scope": self.scope,
            "owner": self.owner,
            "timestamp": self.timestamp,
        }


class ContextManager:
    """Manage isolated context for multi-agent execution.

    Provides scoped context storage with agent-level isolation,
    task-level scoping, and shared state for inter-agent
    coordination.

    Usage:
        ctx = ContextManager()
        ctx.set("target", "192.168.1.1", scope="shared")
        ctx.set("scan_results", [...], scope="agent", owner="scanner")
        target = ctx.get("target")
        results = ctx.get("scan_results", owner="scanner")
    """

    def __init__(self, persist_dir: Optional[str] = None) -> None:
        """Initialize context manager.

        Args:
            persist_dir: Directory for context persistence. If None, in-memory only.
        """
        self._entries: dict[str, ContextEntry] = {}
        self.persist_dir = Path(persist_dir) if persist_dir else None
        if self.persist_dir:
            self.persist_dir.mkdir(parents=True, exist_ok=True)

    def _make_key(self, key: str, scope: str, owner: str) -> str:
        """Create a unique storage key."""
        return f"{scope}:{owner}:{key}" if owner else f"{scope}:{key}"

    def set(self, key: str, value: Any, scope: str = "shared", owner: str = "") -> None:
        """Set a context value.

        Args:
            key: Context key.
            value: Context value.
            scope: Scope level (shared, agent, task).
            owner: Owner identifier.
        """
        storage_key = self._make_key(key, scope, owner)
        self._entries[storage_key] = ContextEntry(
            key=key, value=value, scope=scope, owner=owner,
        )

    def get(self, key: str, scope: str = "shared", owner: str = "", default: Any = None) -> Any:
        """Get a context value.

        Looks up the value by key, scope, and owner. Falls back
        to shared scope if not found in the specified scope.

        Args:
            key: Context key.
            scope: Scope level.
            owner: Owner identifier.
            default: Default value if key not found.

        Returns:
            Context value or default.
        """
        # Try exact scope+owner first
        storage_key = self._make_key(key, scope, owner)
        if storage_key in self._entries:
            return self._entries[storage_key].value

        # Fall back to shared scope
        if scope != "shared":
            shared_key = self._make_key(key, "shared", "")
            if shared_key in self._entries:
                return self._entries[shared_key].value

        return default

    def delete(self, key: str, scope: str = "shared", owner: str = "") -> bool:
        """Delete a context value.

        Args:
            key: Context key.
            scope: Scope level.
            owner: Owner identifier.

        Returns:
            True if the key was found and deleted.
        """
        storage_key = self._make_key(key, scope, owner)
        if storage_key in self._entries:
            del self._entries[storage_key]
            return True
        return False

    def get_scope(self, scope: str, owner: str = "") -> dict[str, Any]:
        """Get all entries in a scope.

        Args:
            scope: Scope level.
            owner: Optional owner filter.

        Returns:
            Dict of key-value pairs in the scope.
        """
        result: dict[str, Any] = {}
        for entry in self._entries.values():
            if entry.scope == scope:
                if not owner or entry.owner == owner:
                    result[entry.key] = entry.value
        return result

    def clear_scope(self, scope: str, owner: str = "") -> int:
        """Clear all entries in a scope.

        Args:
            scope: Scope level.
            owner: Optional owner filter.

        Returns:
            Number of entries cleared.
        """
        to_delete = [
            k for k, v in self._entries.items()
            if v.scope == scope and (not owner or v.owner == owner)
        ]
        for k in to_delete:
            del self._entries[k]
        return len(to_delete)

    def save(self, filename: str = "context.json") -> Optional[str]:
        """Persist context to file.

        Args:
            filename: Output filename.

        Returns:
            Path to saved file, or None if no persist_dir.
        """
        if not self.persist_dir:
            return None

        data = {k: v.to_dict() for k, v in self._entries.items()}
        path = self.persist_dir / filename
        path.write_text(json.dumps(data, indent=2))
        return str(path)

    def load(self, filename: str = "context.json") -> int:
        """Load context from file.

        Args:
            filename: Input filename.

        Returns:
            Number of entries loaded.
        """
        if not self.persist_dir:
            return 0

        path = self.persist_dir / filename
        if not path.exists():
            return 0

        data = json.loads(path.read_text())
        count = 0
        for k, v in data.items():
            self._entries[k] = ContextEntry(**v)
            count += 1
        return count

    def get_all(self) -> dict[str, Any]:
        """Get all context entries."""
        return {k: v.to_dict() for k, v in self._entries.items()}

    def size(self) -> int:
        """Get number of context entries."""
        return len(self._entries)
