"""Overseerr API client."""

from __future__ import annotations

import logging
from typing import Any
from urllib.parse import quote_plus

import httpx

log = logging.getLogger(__name__)


class OverseerrApiClient:
    def __init__(self, base_url: str, api_key: str) -> None:
        if not base_url:
            raise ValueError("Overseerr base URL is required.")
        if not api_key:
            raise ValueError("Overseerr API key is required.")

        self.base_url = base_url.rstrip("/") + "/api/v1"
        self._client = httpx.AsyncClient(headers={"X-Api-Key": api_key})
        log.info(f"OverseerrApiClient initialized for URL: {self.base_url}")

    async def close(self) -> None:
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

        encoded_params: dict[str, Any] | None = None
        if params:
            encoded_params = {}
            for key, value in params.items():
                if isinstance(value, str):
                    encoded_params[key] = quote_plus(value)
                elif isinstance(value, (list, tuple)):
                    encoded_params[key] = [
                        quote_plus(str(v)) if isinstance(v, str) else v for v in value
                    ]
                else:
                    encoded_params[key] = value
            log.debug(f"Overseerr API Request: {method} {url} | Params: {encoded_params}")
        else:
            log.debug(f"Overseerr API Request: {method} {url} | JSON: {json_data}")

        try:
            response = await self._client.request(
                method, url, params=encoded_params, json=json_data
            )
            response.raise_for_status()

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
                "Overseerr API HTTP Error: %s for %s - %s",
                e.response.status_code,
                e.request.url,
                e.response.text,
            )
            try:
                error_detail = e.response.json().get("message", e.response.text)
            except ValueError:
                error_detail = e.response.text or f"Status {e.response.status_code}"
            return (
                f"Error: Overseerr API request failed ({e.response.status_code})."
                f" Details: {error_detail}"
            )
        except httpx.RequestError as e:
            log.error(f"Overseerr API Request Error: {e} for {e.request.url}")
            return f"Error: Failed to connect to Overseerr. Details: {e}"
        except Exception as e:
            log.error(f"Unexpected error during Overseerr API request to {url}: {e}", exc_info=True)
            return f"Error: An unexpected error occurred. Details: {e}"

    async def get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict | list | str:
        return await self._request("GET", endpoint, params=params)

    async def post(
        self,
        endpoint: str,
        json_data: dict[str, Any],
        params: dict[str, Any] | None = None,
    ) -> dict | list | str:
        return await self._request("POST", endpoint, json_data=json_data, params=params)
