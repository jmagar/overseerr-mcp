"""Tests for the consolidated overseerr tool registration."""

from unittest.mock import AsyncMock

import pytest
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from overseerr_mcp.tools.overseerr import register_overseerr_tool, _HELP_TEXT


@pytest.fixture
def mock_client():
    return AsyncMock()


@pytest.fixture
def tool_fn(mock_client):
    """Create a FastMCP instance and get the overseerr tool function."""
    mcp = FastMCP(name="test")
    overseerr_fn = register_overseerr_tool(mcp, mock_client)
    return overseerr_fn, mock_client


def test_help_text_contains_all_domains():
    assert "search" in _HELP_TEXT.lower()
    assert "movie" in _HELP_TEXT.lower()
    assert "tv" in _HELP_TEXT.lower()
    assert "request" in _HELP_TEXT.lower()


async def test_action_help_returns_full_help(tool_fn):
    overseerr_fn, mock_client = tool_fn
    result = await overseerr_fn(action="help")
    assert result == _HELP_TEXT


async def test_action_search_help(tool_fn):
    overseerr_fn, mock_client = tool_fn
    result = await overseerr_fn(action="search", subaction="help")
    assert isinstance(result, str)
    assert "search" in result.lower()


async def test_action_movie_help(tool_fn):
    overseerr_fn, mock_client = tool_fn
    result = await overseerr_fn(action="movie", subaction="help")
    assert isinstance(result, str)
    assert "movie" in result.lower()


async def test_action_tv_help(tool_fn):
    overseerr_fn, mock_client = tool_fn
    result = await overseerr_fn(action="tv", subaction="help")
    assert isinstance(result, str)
    assert "tv" in result.lower()


async def test_action_request_help(tool_fn):
    overseerr_fn, mock_client = tool_fn
    result = await overseerr_fn(action="request", subaction="help")
    assert isinstance(result, str)
    assert "request" in result.lower()


async def test_search_delegates_to_handler(tool_fn):
    overseerr_fn, mock_client = tool_fn
    mock_client.get = AsyncMock(return_value={"results": []})
    await overseerr_fn(action="search", subaction="media", query="Dune")
    mock_client.get.assert_called_once()


async def test_movie_delegates_to_handler(tool_fn):
    overseerr_fn, mock_client = tool_fn
    mock_client.get = AsyncMock(return_value={"id": 1, "title": "Test"})
    await overseerr_fn(action="movie", subaction="details", tmdb_id=1)
    mock_client.get.assert_called_once_with("/movie/1")


async def test_tv_delegates_to_handler(tool_fn):
    overseerr_fn, mock_client = tool_fn
    mock_client.get = AsyncMock(return_value={"id": 1, "name": "Test Show"})
    await overseerr_fn(action="tv", subaction="details", tmdb_id=1)
    mock_client.get.assert_called_once_with("/tv/1")


async def test_request_delegates_to_handler(tool_fn):
    overseerr_fn, mock_client = tool_fn
    mock_client.get = AsyncMock(return_value={"results": []})
    await overseerr_fn(action="request", subaction="failed")
    mock_client.get.assert_called_once()
