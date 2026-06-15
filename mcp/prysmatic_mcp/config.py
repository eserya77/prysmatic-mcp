"""Configuration for the Prysmatic MCP server, read from the environment.

  PRYSMATIC_API_KEY   the API key the tools authenticate with (required).
  PRYSMATIC_API_BASE  API base URL (optional; defaults to production).
"""

from __future__ import annotations

import os

API_BASE = os.environ.get(
    "PRYSMATIC_API_BASE", "https://api.prysmatic-sol.xyz").rstrip("/")
API_KEY = os.environ.get("PRYSMATIC_API_KEY", "")


def require_api_key() -> str:
    """Return the configured API key or raise a readable error if it's missing."""
    if not API_KEY:
        raise RuntimeError(
            "PRYSMATIC_API_KEY is not set. Get an API key from the Prysmatic "
            "dashboard and pass it to the MCP server via its env "
            "(e.g. `claude mcp add prysmatic -e PRYSMATIC_API_KEY=<key> ...`).")
    return API_KEY
