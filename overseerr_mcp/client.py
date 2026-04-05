import logging
import os
from typing import Any

import httpx

log = logging.getLogger(__name__)

# These would be loaded by server.py from .env
OVERSEERR_URL = os.getenv("OVERSEERR_URL")
OVERSEERR_API_KEY = os.getenv("OVERSEERR_API_KEY")


class OverseerrApiClient:
    def __init__(self, base_url: str | None, api_key: str | None):
        if not base_url:
            log.error("Overseerr API client initialized without a base URL.")
            raise ValueError("Overseerr base URL is required.")
        if not api_key:
            log.error("Overseerr API client initialized without an API key.")
            raise ValueError("Overseerr API key is required.")

        self.base_url = base_url.rstrip("/") + "/api/v1"
        self.api_key = api_key
        self._client = httpx.AsyncClient(headers={"X-Api-Key": self.api_key})
        log.info(f"OverseerrApiClient initialized for URL: {self.base_url}")

    async def close(self):
        await self._client.aclose()
        log.info("OverseerrApiClient closed.")

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
    ) -> dict | list | str:
        url = f"{self.base_url}{endpoint}"

        if params:
            log.debug(
                f"Overseerr API Request: {method} {url} | Params: {params} | JSON: {json_data}"
            )
        else:
            log.debug(f"Overseerr API Request: {method} {url} | JSON: {json_data}")

        try:
            response = await self._client.request(method, url, params=params, json=json_data)
            response.raise_for_status()  # Raises HTTPStatusError for 4xx/5xx responses

            # Handle cases where response might be empty
            # (e.g., 204 No Content for a successful POST/DELETE)
            if response.status_code == 204:
                return {
                    "status": "success",
                    "message": "Operation successful, no content returned.",
                }
            if not response.content:
                return {
                    "status": "success",
                    "message": "Operation successful, empty response body.",
                }

            return response.json()
        except httpx.HTTPStatusError as e:
            log.error(
                f"Overseerr API HTTP Error: {e.response.status_code}"
                f" for {e.request.url} - Response: {e.response.text}"
            )
            error_detail = "Unknown error"
            try:
                # Try to parse error from Overseerr if it provides a JSON response
                error_json = e.response.json()
                error_detail = error_json.get("message", e.response.text)
            except ValueError:  # JSONDecodeError is a subclass of ValueError
                error_detail = (
                    e.response.text if e.response.text else f"Status {e.response.status_code}"
                )
            return (
                f"Error: Overseerr API request failed ({e.response.status_code})."
                f" Details: {error_detail}"
            )
        except httpx.RequestError as e:
            log.error(f"Overseerr API Request Error: {e} for {e.request.url}")
            return f"Error: Failed to connect to Overseerr. Details: {e}"
        except Exception as e:  # Catch any other unexpected errors
            log.error(f"Unexpected error during Overseerr API request to {url}: {e}", exc_info=True)
            return f"Error: An unexpected error occurred. Details: {e}"

    async def get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict | list | str:
        return await self._request("GET", endpoint, params=params)

    async def post(
        self, endpoint: str, json_data: dict[str, Any], params: dict[str, Any] | None = None
    ) -> dict | list | str:
        return await self._request("POST", endpoint, json_data=json_data, params=params)
