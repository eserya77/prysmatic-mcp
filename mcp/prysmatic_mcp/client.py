"""Thin httpx client around the Prysmatic REST API.

Every call forwards the configured API key as a Bearer token and turns the common
failure cases into readable errors the model can relay to the user. Each request
spends credits exactly like a direct REST call (the API meters it server-side).
"""

from __future__ import annotations

from typing import Any

import httpx

from .config import API_BASE, require_api_key

_TIMEOUT = 30


def get(path: str, params: dict[str, Any] | None = None) -> Any:
    """GET `path` on the Prysmatic API with the configured key; return parsed JSON.

    Raises RuntimeError with a human-readable message on auth/credit/not-found and
    other HTTP errors, or when the API is unreachable.
    """
    headers = {"Authorization": f"Bearer {require_api_key()}"}
    try:
        resp = httpx.get(f"{API_BASE}{path}", params=params, headers=headers,
                         timeout=_TIMEOUT)
    except httpx.RequestError as exc:
        raise RuntimeError(f"Could not reach the Prysmatic API: {exc}") from exc

    if resp.status_code == 401:
        raise RuntimeError("Invalid or missing API key (401).")
    if resp.status_code == 402:
        raise RuntimeError(
            "Insufficient credits (402). Top up at the Prysmatic dashboard.")
    if resp.status_code == 404:
        raise RuntimeError(f"Not found (404): {_detail(resp)}")
    if resp.status_code >= 400:
        raise RuntimeError(f"API error {resp.status_code}: {_detail(resp)}")
    return resp.json()


def _detail(resp: httpx.Response) -> str:
    try:
        return resp.json().get("detail", resp.text)
    except Exception:
        return resp.text
