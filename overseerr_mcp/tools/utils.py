"""Shared utilities for overseerr tool handlers."""

from __future__ import annotations

from fastmcp.exceptions import ToolError


def validate_subaction(subaction: str, valid_set: set[str], domain: str) -> None:
    """Raise ToolError if subaction is not in valid_set."""
    if subaction not in valid_set:
        raise ToolError(
            f"Invalid subaction '{subaction}' for {domain}. Must be one of: {sorted(valid_set)}"
        )
