# Prysmatic

A Claude Code plugin that bundles:

- the **`prysmatic-api` skill** — teaches Claude the Prysmatic REST API, and
- the **`prysmatic` MCP server** — 5 tools to query tracked Solana wallets and tokens.

The MCP package source lives in [`mcp/`](mcp) and is published on PyPI as
[`prysmatic-mcp`](https://pypi.org/project/prysmatic-mcp/).

## Prerequisites

- An MCP-capable client (e.g. Claude Code).
- [`uv`](https://docs.astral.sh/uv/) on PATH (the plugin runs the server with `uvx`).
- A Prysmatic API key with credits. Export it **before** launching the client:

```bash
# macOS / Linux
export PRYSMATIC_API_KEY=your_key
```
```powershell
# Windows (PowerShell)
$env:PRYSMATIC_API_KEY = "your_key"
```

## Install — plugin (skill + MCP)

In Claude Code:

```
/plugin marketplace add eserya77/prysmatic-mcp
/plugin install prysmatic@prysmatic-mcp
```

Restart when prompted. You get the five MCP tools (`list_wallets`, `wallet_metrics`,
`wallet_holdings`, `tokens_held`, `token_swaps`) plus the `prysmatic-api` skill.

Verify: `/mcp` shows `prysmatic` connected, and `/plugin` lists the plugin.

## Install — MCP only (no plugin)

```
pipx install prysmatic-mcp
claude mcp add prysmatic prysmatic-mcp -e PRYSMATIC_API_KEY=your_key
```

See [`mcp/README.md`](mcp/README.md) for details and the Windows PATH note.

## Install — skill only

Copy [`plugins/prysmatic/skills/prysmatic-api/SKILL.md`](plugins/prysmatic/skills/prysmatic-api/SKILL.md)
into `~/.claude/skills/prysmatic-api/SKILL.md`.

## Layout

```
.claude-plugin/marketplace.json     # marketplace manifest
plugins/prysmatic/                  # the plugin
  .claude-plugin/plugin.json
  .mcp.json                         # registers the MCP via uvx
  skills/prysmatic-api/SKILL.md     # the skill
mcp/                                # MCP package source (published to PyPI)
```
