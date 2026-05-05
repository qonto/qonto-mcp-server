from typing import Optional
import requests
from requests.exceptions import RequestException
import qonto_mcp
from qonto_mcp import mcp


@mcp.tool()
def list_qonto_transaction_attachments(
    transaction_id: str, page: Optional[str] = None, per_page: Optional[str] = None
):
    """
    Retrieves all attachments for a specific transaction from the Qonto API.

    Attachments represent documents like receipts or invoices linked to transactions.

    Note: The download URLs returned are only valid for 30 minutes. If you need to access
    the files after that time, you'll need to call this function again.

    Args:
        transaction_id: UUID of the transaction to retrieve attachments for
        page: Page number for pagination
        per_page: Number of attachments per page

    Example: list_qonto_transaction_attachments(
                transaction_id='aab86d8a-0d4c-4749-9a49-0ada88a9c423'
             )
    """
    url = f"{qonto_mcp.thirdparty_host}/v2/transactions/{transaction_id}/attachments"
    params = {}

    if page:
        params["page"] = page
    if per_page:
        params["per_page"] = per_page

    try:
        response = requests.get(url, headers=qonto_mcp.headers, params=params)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        raise RuntimeError(f"Failed to fetch transaction attachments {str(e)}")


@mcp.tool()
def mark_qonto_transaction_attachment_not_required(transaction_id: str):
    """
    Marks a transaction as not requiring an attachment in the Qonto API.

    Use this when a transaction (e.g. a small expense, refund, or internal
    transfer) does not need a receipt/invoice attached, to clear the
    "attachment required" status.

    Args:
        transaction_id: UUID of the transaction

    Example: mark_qonto_transaction_attachment_not_required(
                transaction_id='aab86d8a-0d4c-4749-9a49-0ada88a9c423'
             )
    """
    url = f"{qonto_mcp.thirdparty_host}/v2/transactions/{transaction_id}"
    payload = {"attachment_required": False}

    try:
        response = requests.patch(url, headers=qonto_mcp.headers, json=payload)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        raise RuntimeError(
            f"Failed to mark transaction as not requiring attachment: {str(e)}"
        )
