import pytest
from fastmcp.exceptions import ToolError
from overseerr_mcp.tools.utils import validate_subaction


def test_valid_subaction_passes():
    validate_subaction("details", {"details", "request", "help"}, "movie")


def test_invalid_subaction_raises_tool_error():
    with pytest.raises(ToolError, match="Invalid subaction 'nope' for movie"):
        validate_subaction("nope", {"details", "request", "help"}, "movie")


def test_error_message_lists_valid_sorted():
    with pytest.raises(ToolError, match="details.*help.*request"):
        validate_subaction("bad", {"details", "request", "help"}, "movie")
