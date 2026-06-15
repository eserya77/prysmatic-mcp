# Prysmatic MCP

Five MCP tools to query the Prysmatic API (tracked wallets and tokens) from Claude
or any MCP client. Each call uses your API key and spends credits, like the REST API.

## Requirements

- Python 3.10+
- A Prysmatic API key with credits (from the dashboard).

## Tools

| Tool | Returns |
|------|---------|
| `list_wallets(page=1)` | Tracked wallets, 25/page |
| `wallet_metrics(alias)` | Metrics for one wallet |
| `wallet_holdings(alias)` | Tokens a wallet holds |
| `tokens_held(min_wallets=2, page=1)` | Tokens held by several wallets |
| `token_swaps(mint, aggregate=False, tracked_only=True)` | Wallet swaps on a token |

## Install

Use **pipx** (isolated venv, puts the command on PATH, won't break other deps):

```
pipx install prysmatic-mcp
```

No pipx yet? `pip install pipx && pipx ensurepath`, then reopen the terminal.

## Add to Claude

```
claude mcp add prysmatic prysmatic-mcp -e PRYSMATIC_API_KEY=<your_key>
```

Notes:
- The `-e` flag must come **last** (it's variadic; before the command it swallows it).
- Verify with `claude mcp list` → `prysmatic ✔ Connected`.

### Windows without pipx

`pip install prysmatic-mcp` installs `prysmatic-mcp.exe` into the user Scripts dir,
which is often **not on PATH** (connect fails). Either use pipx, or pass the full path:

```
claude mcp add prysmatic "%APPDATA%\Python\Python313\Scripts\prysmatic-mcp.exe" -e PRYSMATIC_API_KEY=<your_key>
```

(adjust the Python version in the path).

## Configuration

| Env var | Required | Default |
|---------|----------|---------|
| `PRYSMATIC_API_KEY` | yes | — |
| `PRYSMATIC_API_BASE` | no | `https://api.prysmatic-sol.xyz` |

## Update

```
pipx upgrade prysmatic-mcp
```

## Errors

Tools return a readable message: bad/missing key (401), out of credits (402),
not found (404).
