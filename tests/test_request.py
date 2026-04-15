import pytest
from unittest.mock import AsyncMock
from fastmcp.exceptions import ToolError

from overseerr_mcp.tools._request import _handle_request, _REQUEST_SUBACTIONS, _REQUEST_HELP


@pytest.fixture
def mock_client():
    return AsyncMock()


def test_request_subactions_set():
    assert _REQUEST_SUBACTIONS == {"failed", "help"}


def test_request_help_constant_is_nonempty():
    assert len(_REQUEST_HELP) > 20
    assert "request" in _REQUEST_HELP.lower()


async def test_help_subaction_returns_help_string(mock_client):
    result = await _handle_request("help", 10, 0, client=mock_client)
    assert isinstance(result, str)
    mock_client.get.assert_not_called()


async def test_invalid_subaction_raises(mock_client):
    with pytest.raises(ToolError, match="Invalid subaction 'bad' for request"):
        await _handle_request("bad", 10, 0, client=mock_client)


async def test_failed_calls_api_with_params(mock_client):
    mock_client.get = AsyncMock(return_value={"results": []})
    await _handle_request("failed", 5, 10, client=mock_client)
    mock_client.get.assert_called_once_with(
        "/request",
        params={"take": 5, "skip": 10, "sort": "modified", "filter": "failed"},
    )


async def test_failed_returns_formatted_list(mock_client):
    mock_client.get = AsyncMock(return_value={
        "results": [
            {
                "id": 42,
                "status": 5,
                "media": {"mediaType": "movie", "tmdbId": 999, "title": "BadMovie"},
                "requestedBy": {"displayName": "alice"},
                "createdAt": "2024-01-01T00:00:00Z",
                "modifiedAt": "2024-01-02T00:00:00Z",
            }
        ]
    })
    result = await _handle_request("failed", 10, 0, client=mock_client)
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["requestId"] == 42
    assert result[0]["requested_by"] == "alice"
    assert result[0]["tmdbId"] == 999


async def test_failed_empty_returns_string(mock_client):
    mock_client.get = AsyncMock(return_value={"results": []})
    result = await _handle_request("failed", 10, 0, client=mock_client)
    assert isinstance(result, str)
    assert "No failed" in result


async def test_failed_propagates_error_string(mock_client):
    mock_client.get = AsyncMock(return_value="Error: 500")
    result = await _handle_request("failed", 10, 0, client=mock_client)
    assert result == "Error: 500"
