"""Tests for core.context — ContextManager."""

from __future__ import annotations

import pytest

from agent_stack.core.context import ContextManager


class TestContextManager:
    """Test context management."""

    def test_set_and_get(self) -> None:
        """Should set and retrieve values."""
        ctx = ContextManager()
        ctx.set("target", "192.168.1.1")
        assert ctx.get("target") == "192.168.1.1"

    def test_default_value(self) -> None:
        """Should return default for missing keys."""
        ctx = ContextManager()
        assert ctx.get("missing", default="fallback") == "fallback"

    def test_scoped_context(self) -> None:
        """Should isolate scoped values."""
        ctx = ContextManager()
        ctx.set("key", "shared", scope="shared")
        ctx.set("key", "agent-specific", scope="agent", owner="scanner")

        assert ctx.get("key") == "shared"
        assert ctx.get("key", scope="agent", owner="scanner") == "agent-specific"

    def test_fallback_to_shared(self) -> None:
        """Should fall back to shared scope."""
        ctx = ContextManager()
        ctx.set("key", "shared-value", scope="shared")
        assert ctx.get("key", scope="agent", owner="unknown") == "shared-value"

    def test_delete(self) -> None:
        """Should delete values."""
        ctx = ContextManager()
        ctx.set("key", "value")
        assert ctx.delete("key") is True
        assert ctx.get("key", default="missing") == "missing"

    def test_delete_missing(self) -> None:
        """Should return False for missing keys."""
        ctx = ContextManager()
        assert ctx.delete("nonexistent") is False

    def test_clear_scope(self) -> None:
        """Should clear scope entries."""
        ctx = ContextManager()
        ctx.set("key1", "v1", scope="agent", owner="a")
        ctx.set("key2", "v2", scope="agent", owner="b")
        ctx.set("key3", "v3", scope="shared")

        cleared = ctx.clear_scope("agent")
        assert cleared == 2
        assert ctx.size() == 1

    def test_get_scope(self) -> None:
        """Should get all values in a scope."""
        ctx = ContextManager()
        ctx.set("key1", "v1", scope="agent", owner="scanner")
        ctx.set("key2", "v2", scope="agent", owner="scanner")
        scope = ctx.get_scope("agent", owner="scanner")
        assert len(scope) == 2

    def test_size(self) -> None:
        """Should track entry count."""
        ctx = ContextManager()
        assert ctx.size() == 0
        ctx.set("a", 1)
        ctx.set("b", 2)
        assert ctx.size() == 2

    def test_persistence(self, tmp_path) -> None:
        """Should save and load context."""
        ctx1 = ContextManager(persist_dir=str(tmp_path))
        ctx1.set("target", "10.0.0.1")
        path = ctx1.save()
        assert path is not None

        ctx2 = ContextManager(persist_dir=str(tmp_path))
        loaded = ctx2.load()
        assert loaded == 1
        assert ctx2.get("target") == "10.0.0.1"
