import uuid
import requests
from datetime import datetime
from typing import Any, Dict, List, Optional
from requests.exceptions import RequestException

import qonto_mcp
from qonto_mcp import mcp


_REQUIRED_TRANSFER_FIELDS = ("amount", "credit_iban", "credit_account_name", "reference")


@mcp.tool()
def get_requests(
    current_page: Optional[int] = None,
    per_page: Optional[int] = None,
    status: Optional[str] = None,
    updated_at_from: Optional[datetime] = None,
    updated_at_to: Optional[datetime] = None,
) -> Dict:
    """
    Get requests from Qonto API.

    Args:
        current_page: The current page of results to retrieve.
        per_page: The number of results per page.
        status: Filter requests by status.
        updated_at_from: Filter requests updated from this date.
        updated_at_to: Filter requests updated until this date.

    Example: get_requests(per_page=10, status="pending")
    """
    url = f"{qonto_mcp.thirdparty_host}/v2/requests"
    params = {}
    if current_page is not None:
        params["current_page"] = current_page
    if per_page is not None:
        params["per_page"] = per_page
    if status is not None:
        params["status"] = status
    if updated_at_from is not None:
        params["updated_at_from"] = updated_at_from.isoformat()
    if updated_at_to is not None:
        params["updated_at_to"] = updated_at_to.isoformat()

    try:
        response = requests.get(url, headers=qonto_mcp.headers, params=params)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        raise RuntimeError(f"Error fetching requests: {str(e)}")


@mcp.tool()
def get_request(request_id: str) -> Dict:
    """
    Get a specific request from Qonto API.

    Args:
        request_id: The ID of the request to retrieve.

    Example: get_request(request_id="a1b2c3d4-5678-90ab-cdef-ghijklmnopqr")
    """
    url = f"{qonto_mcp.thirdparty_host}/v2/requests/{request_id}"

    try:
        response = requests.get(url, headers=qonto_mcp.headers)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        raise RuntimeError(f"Error fetching request: {str(e)}")


@mcp.tool()
def create_qonto_multi_transfer_request(
    note: str,
    transfers: List[Dict[str, Any]],
    scheduled_date: Optional[str] = None,
    debit_iban: Optional[str] = None,
) -> Dict:
    """
    Create a multi-transfer request in Qonto (the canonical "expense report" /
    batch reimbursement flow under Expense Management → Requests).

    Submits a batch of one or more transfers in a single approval request. Use
    this to reimburse an employee for several receipts at once, or to pay a
    list of suppliers in one approval cycle. All amounts are in EUR.

    Args:
        note: Free-text note for the request, shown to the approver (≤140 chars).
        transfers: List of 1–400 transfer items. Each item is a dict with:
            - amount (str, required): decimal with 2 digits, e.g. "12.34"
            - credit_iban (str, required): IBAN of the recipient (ISO 13616)
            - credit_account_name (str, required): recipient name (≤140 chars)
            - reference (str, required): payment reference (≤140 chars)
            - attachment_ids (List[str], optional): UUIDs of receipts/invoices
              already known to Qonto (e.g. from list_qonto_transaction_attachments)
        scheduled_date: Optional execution date (YYYY-MM-DD); defaults to the
            current/next banking day.
        debit_iban: Optional IBAN of the Qonto account to debit; defaults to
            the organization's main account.

    Example: create_qonto_multi_transfer_request(
                note="March travel expenses",
                transfers=[
                    {
                        "amount": "42.00",
                        "credit_iban": "FR7630006000011234567890189",
                        "credit_account_name": "Alice Dupont",
                        "reference": "Taxi 2026-03-12",
                    }
                ],
             )
    """
    if len(note) > 140:
        raise ValueError("note must be 140 characters or fewer.")
    if not 1 <= len(transfers) <= 400:
        raise ValueError("transfers must contain between 1 and 400 items.")

    payload_transfers: List[Dict[str, Any]] = []
    for index, transfer in enumerate(transfers):
        missing = [field for field in _REQUIRED_TRANSFER_FIELDS if not transfer.get(field)]
        if missing:
            raise ValueError(
                f"transfers[{index}] is missing required field(s): {', '.join(missing)}"
            )
        if len(transfer["credit_account_name"]) > 140:
            raise ValueError(f"transfers[{index}].credit_account_name must be ≤140 chars.")
        if len(transfer["reference"]) > 140:
            raise ValueError(f"transfers[{index}].reference must be ≤140 chars.")

        item: Dict[str, Any] = {
            "amount": transfer["amount"],
            "currency": "EUR",
            "credit_iban": transfer["credit_iban"],
            "credit_account_name": transfer["credit_account_name"],
            "credit_account_currency": "EUR",
            "reference": transfer["reference"],
        }
        if transfer.get("attachment_ids"):
            item["attachment_ids"] = transfer["attachment_ids"]
        payload_transfers.append(item)

    body: Dict[str, Any] = {"note": note, "transfers": payload_transfers}
    if scheduled_date is not None:
        body["scheduled_date"] = scheduled_date
    if debit_iban is not None:
        body["debit_iban"] = debit_iban

    url = f"{qonto_mcp.thirdparty_host}/v2/requests/multi_transfers"
    headers = {**qonto_mcp.headers, "X-Qonto-Idempotency-Key": str(uuid.uuid4())}

    try:
        response = requests.post(url, headers=headers, json={"request_multi_transfer": body})
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        raise RuntimeError(f"Failed to create multi-transfer request: {str(e)}")
