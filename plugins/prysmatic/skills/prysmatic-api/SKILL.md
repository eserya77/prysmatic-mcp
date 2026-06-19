---
name: prysmatic-api
description: Query the Prysmatic REST API for tracked Solana wallet and token analytics — list tracked wallets and their PnL/behavior metrics, a wallet's current holdings, tokens co-held by N tracked wallets, and tracked-wallet swaps on a token. Use whenever the user wants Prysmatic tracked-wallet data, smart-money holdings, or token co-holding analysis.
---

# Prysmatic API

Read-only REST API over tracked Solana wallets and the tokens they trade. Wallets
are exposed as opaque `W{n}` aliases (never real addresses); amounts and timestamps
are display-salted. On-chain locators (signatures, slots, pools, counterparties) are
never exposed.

## Auth

Bearer API key on every request. Each call spends prepaid credits (wallets = 1,
tokens/swaps = 3). Out of credits → `402`.

```
Authorization: Bearer <API_KEY>
```

- Base URL: `https://api.prysmatic-sol.xyz`
- Get a key + load credits from the Prysmatic dashboard.

## Endpoints

| Method | Path | Query params | Cost | Returns |
|--------|------|--------------|------|---------|
| GET | `/wallets` | `page` (1+) | 1 | Tracked wallets, 25/page, ordered W1..WN. |
| GET | `/wallets/{alias}/metrics` | — | 1 | Full metrics for one wallet. |
| GET | `/wallets/{alias}/holdings` | — | 1 | Tokens the wallet currently holds. |
| GET | `/tokens/held` | `min_wallets` (default 2), `page` | 3 | Tokens held by ≥ N tracked wallets, ordered by co-holder count desc. |
| GET | `/tokens/{mint}/swaps` | `aggregate` (bool), `tracked_only` (bool, default true) | 3 | Raw swap rows, or one row per wallet when `aggregate=true`. |

`{alias}` is a `W{n}` id (e.g. `W12`). `{mint}` is a Solana mint address. Paginated
responses include `total` and `has_more`.

## Response shapes

### `GET /wallets` and `GET /wallets/{alias}/metrics`

Each wallet item has four nested groups plus `computed_at` (unix timestamp):

```
identity:  { wallet, tracked, score, status }
pnl:       { sol_balance, pnl_sol, sol_bought, sol_sold, sol_invested_open, unrealized_token_count }
activity:  { total_trades, buys, sells, transfers_in, transfers_out, sol_received, sol_sent, unique_tokens_traded }
behavior:  { winrate, loserate, avg_holding_time, avg_time_to_almost_full_exit,
             avg_buy_amount, avg_sell_amount, quick_sells, sold_more_than_bought, active_times }
```

### `GET /wallets/{alias}/holdings`

```
wallet: "W{n}"
tokens: [
  {
    token:    { address, decimals }
    position: { balance, tokens_acquired, tokens_held, sol_invested }
    timing:   { first_activity_at, last_activity_at, holding_time }
  }
]
```

### `GET /tokens/held`

```
min_wallets, page, page_size, total, has_more
items: [
  {
    token:     { address, decimals }
    holders:   { wallet_count, wallets: ["W{n}", ...] }   # full alias list
    aggregate: { tokens_held, sol_invested }
  }
]
```

### `GET /tokens/{mint}/swaps` (raw, `aggregate=false`)

```
mint, count
items: [
  { block_time, wallet, side, base_mint, base_symbol, base_amount, base_decimals,
    quote_mint, quote_amount, program, confidence, quote_mismatch }
]
```

`base_symbol` may be null. Amounts and timestamps are salted.

### `GET /tokens/{mint}/swaps?aggregate=true`

One row per wallet that traded the token:

```
mint, tracked_wallets
wallets: [
  { wallet, alias, buys, sells, base_bought, base_sold, base_net,
    sol_in, sol_out, pct_held, first_buy_time, last_trade_time, entry_mcap }
]
```

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
- `429` rate limited

## MCP

These endpoints are also packaged as an MCP server (`prysmatic-mcp` on PyPI), which
exposes them as the tools `list_wallets`, `wallet_metrics`, `wallet_holdings`,
`tokens_held`, `token_swaps`. Prefer the MCP tools when they're available in the
session; otherwise call the REST endpoints above directly.

## WebSocket — live trade feed

`wss://api.prysmatic-sol.xyz/ws`

### Auth (pick one)

| Mode | How | Channels available |
|------|-----|--------------------|
| API key (metered) | `Sec-WebSocket-Protocol: bearer, <api_key>` | `trades` only |
| JWT subscriber | `?token=<jwt>` (active subscription) | all channels |
| Public demo | allowed Origin, no auth | `trades`, `scoring`, `signals` (read-only) |

The API key must **not** go in the URL — pass it as the second subprotocol so it
stays out of proxy logs. One active connection per key; opening a second one
immediately kicks the first (`{"type":"superseded"}`).

### Credit metering

Each payload delivered costs **1 credit**. Credits are tracked in-memory per
connection and flushed to the DB in batches. When credits hit zero the server
sends `{"type":"balance_exhausted"}` and closes (`code 1008`). A filtered-out
trade (wallet not in your filter) is neither sent nor charged.

### Client messages

After connecting, send JSON frames to control subscriptions:

```json
{ "action": "subscribe",   "channels": ["trades"], "wallets": ["W12", "W37"] }
{ "action": "unsubscribe", "channels": ["trades"] }
```

- `channels`: list of channel names (max 8 per connection).
- `wallets`: optional list of W{n} aliases to filter to (max 100). Omit to
  receive all wallets. Re-sending `subscribe` replaces the current filter.

### Server messages

**Heartbeat** — sent every ~30 s of client silence; ignore or pong as needed:
```json
{ "type": "ping" }
```

**`trades` channel** — one message per swap of a tracked wallet:
```json
{
  "channel": "trades",
  "data": {
    "block_time":    1718000000,   // unix, salted ±3–16 s
    "wallet":        "W12",        // opaque alias
    "side":          "buy",        // "buy" | "sell"
    "mint":          "<base_mint>",
    "token_amount":  "1234567",    // salted ±10%, raw units (apply decimals)
    "decimals":      6,
    "sol_amount":    0.45,         // SOL (not lamports), salted ±10%
    "quote_mint":    "<mint>",     // null for native-SOL pairs
    "quote_amount":  "450000000",  // salted ±10%
    "program":       "pumpfun"
  }
}
```

Amounts and timestamps are display-salted; on-chain locators (signature, slot,
pool, counterparty) are never included.

### Close codes

| Code | Meaning |
|------|---------|
| 1008 | Auth failed, no credits, or policy violation |
| 1009 | Client message too large (> 4 KB) |
| 1013 | Server at capacity — retry later |

### Minimal JS example

```js
const ws = new WebSocket("wss://api.prysmatic-sol.xyz/ws", ["bearer", API_KEY]);

ws.onopen = () => {
  ws.send(JSON.stringify({ action: "subscribe", channels: ["trades"] }));
};

ws.onmessage = ({ data }) => {
  const msg = JSON.parse(data);
  if (msg.type === "balance_exhausted") { /* top up */ return; }
  if (msg.channel === "trades") console.log(msg.data);
};
```

## Notes

- Wallet aliases are stable but anonymized; do not attempt to de-anonymize them.
- Per-wallet swap/transfer history is intentionally not exposed via REST (de-anonymization risk); use the WebSocket for live trades.
