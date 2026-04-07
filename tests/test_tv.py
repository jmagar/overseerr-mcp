import pytest
from unittest.mock import AsyncMock
from fastmcp.exceptions import ToolError

from overseerr_mcp.tools._tv import _handle_tv, _TV_SUBACTIONS, _TV_HELP


@pytest.fixture
def mock_client():
    return AsyncMock()


def test_tv_subactions_set():
    assert _TV_SUBACTIONS == {"details", "request", "help"}


def test_tv_help_constant_is_nonempty():
    assert len(_TV_HELP) > 20
    assert "tv" in _TV_HELP.lower()


async def test_help_subaction_returns_help_string(mock_client):
    result = await _handle_tv("help", None, None, client=mock_client)
    assert isinstance(result, str)
    mock_client.get.assert_not_called()


async def test_invalid_subaction_raises(mock_client):
    with pytest.raises(ToolError, match="Invalid subaction 'bad' for tv"):
        await _handle_tv("bad", None, None, client=mock_client)


async def test_details_requires_tmdb_id(mock_client):
    with pytest.raises(ToolError, match="tmdb_id is required"):
        await _handle_tv("details", None, None, client=mock_client)


async def test_request_requires_tmdb_id(mock_client):
    with pytest.raises(ToolError, match="tmdb_id is required"):
        await _handle_tv("request", None, None, client=mock_client)


async def test_details_returns_api_response(mock_client):
    mock_client.get = AsyncMock(return_value={"id": 1396, "name": "Breaking Bad"})
    result = await _handle_tv("details", 1396, None, client=mock_client)
    assert result == {"id": 1396, "name": "Breaking Bad"}
    mock_client.get.assert_called_once_with("/tv/1396")


async def test_request_all_seasons_when_none(mock_client):
    mock_client.post = AsyncMock(return_value={
        "id": 10, "status": 1, "media": {"tmdbId": 1396}
    })
    await _handle_tv("request", 1396, None, client=mock_client)
    mock_client.post.assert_called_once_with(
        "/request",
        json_data={"mediaType": "tv", "mediaId": 1396, "seasons": "all"},
    )


async def test_request_specific_seasons(mock_client):
    mock_client.post = AsyncMock(return_value={
        "id": 11, "status": 1, "media": {"tmdbId": 1396}
    })
    await _handle_tv("request", 1396, [1, 2], client=mock_client)
    mock_client.post.assert_called_once_with(
        "/request",
        json_data={"mediaType": "tv", "mediaId": 1396, "seasons": [1, 2]},
    )


async def test_request_propagates_error_string(mock_client):
    mock_client.post = AsyncMock(return_value="Error: already exists")
    result = await _handle_tv("request", 1396, None, client=mock_client)
    assert result == "Error: already exists"
