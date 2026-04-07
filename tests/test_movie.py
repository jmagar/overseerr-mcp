from unittest.mock import AsyncMock

import pytest
from fastmcp.exceptions import ToolError

from overseerr_mcp.tools._movie import _MOVIE_HELP, _MOVIE_SUBACTIONS, _handle_movie


@pytest.fixture
def mock_client():
    return AsyncMock()


def test_movie_subactions_set():
    assert _MOVIE_SUBACTIONS == {"details", "request", "help"}


def test_movie_help_constant_is_nonempty():
    assert len(_MOVIE_HELP) > 20
    assert "movie" in _MOVIE_HELP.lower()


async def test_help_subaction_returns_help_string(mock_client):
    result = await _handle_movie("help", None, client=mock_client)
    assert isinstance(result, str)
    mock_client.get.assert_not_called()
    mock_client.post.assert_not_called()


async def test_invalid_subaction_raises(mock_client):
    with pytest.raises(ToolError, match="Invalid subaction 'bad' for movie"):
        await _handle_movie("bad", None, client=mock_client)


async def test_details_requires_tmdb_id(mock_client):
    with pytest.raises(ToolError, match="tmdb_id is required"):
        await _handle_movie("details", None, client=mock_client)


async def test_request_requires_tmdb_id(mock_client):
    with pytest.raises(ToolError, match="tmdb_id is required"):
        await _handle_movie("request", None, client=mock_client)


async def test_details_returns_api_response(mock_client):
    mock_client.get = AsyncMock(return_value={"id": 27205, "title": "Inception"})
    result = await _handle_movie("details", 27205, client=mock_client)
    assert result == {"id": 27205, "title": "Inception"}
    mock_client.get.assert_called_once_with("/movie/27205")


async def test_details_propagates_error_string(mock_client):
    mock_client.get = AsyncMock(return_value="Error: 404")
    result = await _handle_movie("details", 27205, client=mock_client)
    assert result == "Error: 404"


async def test_request_posts_correct_payload(mock_client):
    mock_client.post = AsyncMock(return_value={
        "id": 99, "status": 1, "media": {"tmdbId": 27205}
    })
    result = await _handle_movie("request", 27205, client=mock_client)
    assert result["id"] == 99
    mock_client.post.assert_called_once_with(
        "/request", json_data={"mediaType": "movie", "mediaId": 27205}
    )


async def test_request_propagates_error_string(mock_client):
    mock_client.post = AsyncMock(return_value="Error: already requested")
    result = await _handle_movie("request", 27205, client=mock_client)
    assert result == "Error: already requested"
