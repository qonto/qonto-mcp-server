# qonto skill

This repository is now a minimal agent skill for read-only Qonto access.

For this use case, a skill is the better fit:

- It keeps the integration local and lightweight.
- It uses one deterministic script instead of an MCP transport stack.
- It matches the actual behavior of the project: direct API reads with a small amount of parameter mapping.
- It is easier to audit, easier to maintain, and easier to extend if richer finance-specific logic is added later.

MCP would make more sense if this project needed to serve many MCP clients or if it were going to add substantial higher-level behavior on top of the raw Qonto API.

## layout

- `SKILL.md`
- `scripts/qonto.sh`

## usage

Set the required environment variables:

```bash
export QONTO_API_KEY=...
export QONTO_ORGANIZATION_ID=...
```

Optional:

```bash
export QONTO_THIRDPARTY_HOST=https://thirdparty.qonto.com
export QONTO_STAGING_TOKEN=...
```

Required tools:

```bash
curl
jq
```

Inspect the available operations:

```bash
bash scripts/qonto.sh list-operations
```

Inspect one operation:

```bash
bash scripts/qonto.sh describe get_qonto_transaction
```

Execute an operation:

```bash
bash scripts/qonto.sh call get_qonto_transaction --params '{"transaction_id":"...","includes":["labels","attachments"]}'
```

The script returns normalized JSON with:

- `ok`
- `operation`
- `request`
- `data` on success
- `error` on failure

To use this inside another repository, place the directory under `.agents/skills/qonto` or install it as a standalone skill source.
