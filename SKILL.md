---
name: qonto
description: Use this skill when a user needs read-only access to Qonto data from an API key and organization ID. Use strict operation schemas from the local script and never invent parameter names. It covers organization details, transactions, transaction attachments, external transfers, beneficiaries, attachments, labels, memberships, client and supplier invoices, credit notes, statements, clients, and approval requests through one local shell script that returns normalized JSON.
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

2. Inspect one operation immediately before calling it. Do not assume parameter names from memory:

```bash
bash scripts/qonto.sh describe get_qonto_transactions
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

## Required execution rules

- Never call an operation with guessed params. Use only the exact parameter names returned by `describe`.
- Never call `get_qonto_transactions` with empty params. `bank_account_id` is required.
- For "latest transactions" requests, use this order:
  1. `get_qonto_organization` to fetch `bank_accounts[].id`.
  2. `get_qonto_transactions` with `{"bank_account_id":"...","per_page":N}`.
- For `get_qonto_transactions`, valid optional keys are:
  - `page`
  - `current_page`
  - `per_page`
  - `updated_at_from`
  - `updated_at_to`
  - `emitted_at_from`
  - `emitted_at_to`
  - `settled_at_from`
  - `settled_at_to`
  - `sort_by`
- Do not use `sort`. The accepted key is `sort_by`.
- If the API returns `422` after adding optional filters or sorting, retry once with only `bank_account_id` and `per_page`.
- If a call fails with `validation_error` and `Unknown parameters`, remove unsupported keys and retry with supported keys listed in the error.

## Notes

- Keep credentials in environment variables. Do not echo them back to the user.
- The script is read-only and only performs `GET` requests.
- Attachment and statement download operations return Qonto’s response payload, which may include short-lived signed URLs.
- Pagination stays explicit. Re-run with `page`, `per_page`, `current_page`, or other supported query params as needed.
- If the user asks for unsupported behavior, say the skill only covers the current read-only endpoints and stop there.
