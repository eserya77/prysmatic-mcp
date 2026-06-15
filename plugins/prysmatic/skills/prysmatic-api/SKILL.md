---
name: prysmatic-api
description: Query the Prysmatic REST API for tracked Solana wallet and token analytics — list tracked wallets and their PnL/behavior metrics, a wallet's current holdings, tokens co-held by N tracked wallets, and tracked-wallet swaps on a token. Use whenever the user wants Prysmatic tracked-wallet data, smart-money holdings, or token co-holding analysis.
---

# Prysmatic API

Read-only REST API over tracked Solana wallets and the tokens they trade. Wallets
are exposed as opaque `W{n}` aliases (never real addresses); amounts and timestamps
are display-salted. There is no symbol/name data.

## Auth

Bearer API key on every request. Each call spends prepaid credits (wallets = 1,
tokens/swaps = 3). Out of credits → `402`.

```
Authorization: Bearer <API_KEY>
```

- Base URL: `https://api.prysmatic-sol.xyz`
- Get a key + load credits from the Prysmatic dashboard.

## Endpoints

| Method | Path | Query params | Returns |
|--------|------|--------------|---------|
| GET | `/wallets` | `page` (1+) | Tracked wallets, 25/page, ordered W1..WN. Each item: `identity / pnl / activity / behavior`. |
| GET | `/wallets/{alias}/metrics` | — | Full metrics for one wallet (same nested shape). |
| GET | `/wallets/{alias}/holdings` | — | Tokens the wallet currently holds (`token / position / timing`). |
| GET | `/tokens/held` | `min_wallets` (default 2), `page` | Tokens held by ≥ N tracked wallets, ordered by co-holder count desc. |
| GET | `/tokens/{mint}/swaps` | `aggregate` (bool), `tracked_only` (bool) | Raw swap rows, or one row per wallet when `aggregate=true`. |

`{alias}` is a `W{n}` id (e.g. `W12`). `{mint}` is a Solana mint address. Paginated
responses include `total` and `has_more`.

## Examples

```bash
# Tracked wallets, page 1
curl -s "https://api.prysmatic-sol.xyz/wallets?page=1" -H "Authorization: Bearer $KEY"

# Tokens co-held by 4+ tracked wallets
curl -s "https://api.prysmatic-sol.xyz/tokens/held?min_wallets=4" -H "Authorization: Bearer $KEY"

# Per-wallet aggregate of swaps on a token
curl -s "https://api.prysmatic-sol.xyz/tokens/<mint>/swaps?aggregate=true" -H "Authorization: Bearer $KEY"
```

## Errors

- `401` invalid/missing key
- `402` insufficient credits (top up at the dashboard)
- `404` unknown wallet/mint

## MCP

These endpoints are also packaged as an MCP server (`prysmatic-mcp` on PyPI), which
exposes them as the tools `list_wallets`, `wallet_metrics`, `wallet_holdings`,
`tokens_held`, `token_swaps`. Prefer the MCP tools when they're available in the
session; otherwise call the REST endpoints above directly.

## Notes

- The live trade feed is a metered WebSocket (`/ws`), not part of this skill.
- Wallet aliases are stable but anonymized; do not attempt to de-anonymize them.
