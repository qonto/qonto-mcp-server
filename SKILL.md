---
name: qonto
description: Use this skill when a user needs read-only access to Qonto data from an API key and organization ID. It covers organization details, transactions, transaction attachments, external transfers, beneficiaries, attachments, labels, memberships, client and supplier invoices, credit notes, statements, clients, and approval requests through one local shell script that returns normalized JSON.
---

# Qonto

Use this skill for direct Qonto API reads. Do not use it for write operations or approval flows.

## When to use it

- The user wants data from Qonto and can provide `QONTO_API_KEY` and `QONTO_ORGANIZATION_ID`.
- The task is a read-only lookup over the existing Qonto third-party API.
- A thin MCP transport would add no value over one script call.

## Required environment

- `QONTO_API_KEY`
- `QONTO_ORGANIZATION_ID`

Optional:

- `QONTO_THIRDPARTY_HOST`
- `QONTO_STAGING_TOKEN`

If `QONTO_THIRDPARTY_HOST` is unset, the script uses `https://thirdparty.qonto.com`.

This skill expects `curl` and `jq` to be available.

## Workflow

1. List the available operations when you need to inspect the surface:

```bash
bash scripts/qonto.sh list-operations
```

2. Inspect one operation before calling it when you need the parameter names:

```bash
bash scripts/qonto.sh describe get_qonto_transaction
```

3. Execute the operation with JSON params:

```bash
bash scripts/qonto.sh call get_qonto_transaction --params '{"transaction_id":"...","includes":["labels","attachments"]}'
```

4. Return the relevant JSON fields to the user. The script always emits normalized JSON with:

- `ok`
- `operation`
- `request`
- `data` on success
- `error` on failure

## Notes

- Keep credentials in environment variables. Do not echo them back to the user.
- The script is read-only and only performs `GET` requests.
- Attachment and statement download operations return Qonto’s response payload, which may include short-lived signed URLs.
- Pagination stays explicit. Re-run with `page`, `per_page`, `current_page`, or other supported query params as needed.
- If the user asks for unsupported behavior, say the skill only covers the current read-only endpoints and stop there.
