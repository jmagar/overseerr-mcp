from unittest.mock import AsyncMock

import pytest
from fastmcp.exceptions import ToolError

from overseerr_mcp.tools._search import _SEARCH_HELP, _SEARCH_SUBACTIONS, _handle_search


@pytest.fixture
def mock_client():
    client = AsyncMock()
    return client


def test_search_subactions_set():
    assert _SEARCH_SUBACTIONS == {"media", "help"}


def test_search_help_constant_is_nonempty():
    assert len(_SEARCH_HELP) > 20
    assert "search" in _SEARCH_HELP.lower()


async def test_help_subaction_returns_help_string(mock_client):
    result = await _handle_search("help", None, None, client=mock_client)
    assert isinstance(result, str)
    assert "search" in result.lower()
    mock_client.get.assert_not_called()


async def test_invalid_subaction_raises(mock_client):
    with pytest.raises(ToolError, match="Invalid subaction 'bad' for search"):
        await _handle_search("bad", None, None, client=mock_client)


async def test_media_requires_query(mock_client):
    with pytest.raises(ToolError, match="query is required"):
        await _handle_search("media", None, None, client=mock_client)


async def test_media_returns_filtered_results(mock_client):
    mock_client.get = AsyncMock(
        return_value={
            "results": [
                {
                    "id": 1,
                    "mediaType": "movie",
                    "title": "Dune",
                    "releaseDate": "2021-10-22",
                    "overview": "Sand",
                    "posterPath": "/dune.jpg",
                },
                {
                    "id": 2,
                    "mediaType": "tv",
                    "name": "Dune TV",
                    "firstAirDate": "2022-01-01",
                    "overview": "More sand",
                    "posterPath": "/tv.jpg",
                },
            ]
        }
    )
    result = await _handle_search("media", "Dune", "movie", client=mock_client)
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["tmdbId"] == 1
    assert result[0]["mediaType"] == "movie"


async def test_media_no_filter_returns_all(mock_client):
    mock_client.get = AsyncMock(
        return_value={
            "results": [
                {
                    "id": 1,
                    "mediaType": "movie",
                    "title": "Dune",
                    "releaseDate": "2021-10-22",
                    "overview": "Sand",
                    "posterPath": "/dune.jpg",
                },
                {
                    "id": 2,
                    "mediaType": "tv",
                    "name": "Dune TV",
                    "firstAirDate": "2022-01-01",
                    "overview": "More sand",
                    "posterPath": "/tv.jpg",
                },
            ]
        }
    )
    result = await _handle_search("media", "Dune", None, client=mock_client)
    assert len(result) == 2


async def test_media_returns_no_results_string(mock_client):
    mock_client.get = AsyncMock(return_value={"results": []})
    result = await _handle_search("media", "xyzzy", None, client=mock_client)
    assert isinstance(result, str)
    assert "No" in result


async def test_media_propagates_client_error_string(mock_client):
    mock_client.get = AsyncMock(return_value="Error: connection refused")
    result = await _handle_search("media", "Dune", None, client=mock_client)
    assert result == "Error: connection refused"
