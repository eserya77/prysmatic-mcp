"""Prysmatic MCP server.

Exposes the credit-metered Prysmatic REST data endpoints (wallets + tokens) as
MCP tools. Runs over stdio, so it plugs straight into Claude Desktop / Code.

Configure via env:
  PRYSMATIC_API_KEY   your API key (required)
  PRYSMATIC_API_BASE  API base URL (optional; defaults to production)

Add to Claude:
  claude mcp add prysmatic -e PRYSMATIC_API_KEY=<your_key> -- prysmatic-mcp
"""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from . import client

mcp = FastMCP("prysmatic")


@mcp.tool()
def list_wallets(page: int = 1) -> dict[str, Any]:
    """List tracked wallets (opaque W{n} aliases), 25 per page, ordered W1..WN.

    Each item groups identity / pnl / activity / behavior metrics. Use `page` to
    paginate; the response includes `total` and `has_more`.
    """
    return client.get("/wallets", {"page": page})


@mcp.tool()
def wallet_metrics(alias: str) -> dict[str, Any]:
    """Full metrics for a single tracked wallet.

    `alias` is the public W{n} id (e.g. "W12"), never a real address. Returns the
    identity / pnl / activity / behavior groups for that wallet.
    """
    return client.get(f"/wallets/{alias}/metrics")


@mcp.tool()
def wallet_holdings(alias: str) -> dict[str, Any]:
    """Tokens a tracked wallet currently holds, derived from our swap data.

    `alias` is the public W{n} id. Returns one entry per held token with its
    position and timing. Symbols/names are intentionally omitted.
    """
    return client.get(f"/wallets/{alias}/holdings")


@mcp.tool()
def tokens_held(min_wallets: int = 2, page: int = 1) -> dict[str, Any]:
    """Tokens currently held by at least `min_wallets` tracked wallets.

    25 per page, ordered by how many wallets co-hold each token (desc). The
    response includes `total` and `has_more`.
    """
    return client.get("/tokens/held", {"min_wallets": min_wallets, "page": page})


@mcp.tool()
def token_swaps(mint: str, aggregate: bool = False,
                tracked_only: bool = True) -> dict[str, Any]:
    """Tracked-wallet swaps on a single token `mint`.

    With `aggregate=true`, returns one row per wallet (sol in/out, % held, entry
    mcap). Otherwise returns the raw swap rows (amounts and times are salted).
    `tracked_only` applies to the raw mode (tracked wallets only when true).
    """
    return client.get(f"/tokens/{mint}/swaps",
                      {"aggregate": aggregate, "tracked_only": tracked_only})


def main() -> None:
    """Console-script entry point: run the server over stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
