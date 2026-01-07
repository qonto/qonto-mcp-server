import requests
from typing import Optional, List
import qonto_mcp
from qonto_mcp import mcp


@mcp.tool()
def get_qonto_transactions(
    bank_account_id: str,
    page: Optional[int] = None,
    per_page: Optional[int] = None,
    settled_at_from: Optional[str] = None,
    settled_at_to: Optional[str] = None,
    status: Optional[str] = None,
    side: Optional[str] = None,
    sort_by: Optional[str] = None,
):
    """
    Retrieves transactions from the Qonto API for a specific bank account.

    Args:
        bank_account_id: UUID of the bank account
        page: Page number for pagination (default: 1)
        per_page: Number of transactions per page (max: 100)
        settled_at_from: Filter transactions settled after this date (ISO 8601)
        settled_at_to: Filter transactions settled before this date (ISO 8601)
        status: Filter by status (pending, completed, declined)
        side: Filter by side (credit, debit)
        sort_by: Sort order (settled_at:asc, settled_at:desc, updated_at:asc, updated_at:desc)

    Example: get_qonto_transactions(
                bank_account_id='0193f298-d9f3-7b77-8566-ce356449d7f3',
                settled_at_from='2025-01-01T00:00:00Z',
                settled_at_to='2025-12-31T23:59:59Z',
                page=1
             )
    """
    url = f"{qonto_mcp.thirdparty_host}/v2/transactions"
    params = {"bank_account_id": bank_account_id}

    if page is not None:
        params["page"] = page
    if per_page is not None:
        params["per_page"] = per_page
    if settled_at_from is not None:
        params["settled_at_from"] = settled_at_from
    if settled_at_to is not None:
        params["settled_at_to"] = settled_at_to
    if status is not None:
        params["status"] = status
    if side is not None:
        params["side"] = side
    if sort_by is not None:
        params["sort_by"] = sort_by

    try:
        response = requests.get(url, headers=qonto_mcp.headers, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return f"Error fetching Qonto transactions: {str(e)}"


@mcp.tool()
def get_qonto_transaction(transaction_id: str, includes: list = None):
    """
    Retrieves a specific transaction from the Qonto API with optional related resources.
    
    This returns detailed information about a transaction including amounts, dates,
    counterparty details, and operation type.

    Args:
        transaction_id: UUID of the transaction to retrieve
        includes: Optional list of related resources to include. Valid options are:
                 'vat_details', 'labels', 'attachments'

    Example: get_qonto_transaction(
                transaction_id='7b7a5ed6-3903-4782-889d-b4f64bd7bef9', 
                includes=['labels', 'attachments']
             )
    """
    url = f"{qonto_mcp.thirdparty_host}/v2/transactions/{transaction_id}"
    params = {}
    
    if includes:
        for include in includes:
            params.setdefault("includes[]", []).append(include)

    try:
        response = requests.get(url, headers=qonto_mcp.headers, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return f"Error fetching transaction: {str(e)}"


@mcp.tool()
def get_all_qonto_transactions(
    bank_account_id: str,
    settled_at_from: Optional[str] = None,
    settled_at_to: Optional[str] = None,
    status: Optional[str] = None,
    side: Optional[str] = None,
    sort_by: Optional[str] = None,
) -> dict:
    """
    Fetches ALL transactions by iterating through all pages.

    Args:
        bank_account_id: UUID of the bank account
        settled_at_from: Filter transactions settled after this date (ISO 8601)
        settled_at_to: Filter transactions settled before this date (ISO 8601)
        status: Filter by status (pending, completed, declined)
        side: Filter by side (credit, debit)
        sort_by: Sort order (settled_at:asc, settled_at:desc, updated_at:asc, updated_at:desc)

    Returns:
        Dict with transactions list and metadata.

    Example: get_all_qonto_transactions(
                bank_account_id='0193f298-d9f3-7b77-8566-ce356449d7f3',
                settled_at_from='2025-01-01T00:00:00Z',
                settled_at_to='2025-12-31T23:59:59Z'
             )
    """
    all_transactions = []
    page = 1
    total_pages = 1

    try:
        while page <= total_pages:
            result = get_qonto_transactions(
                bank_account_id=bank_account_id,
                page=page,
                per_page=100,
                settled_at_from=settled_at_from,
                settled_at_to=settled_at_to,
                status=status,
                side=side,
                sort_by=sort_by,
            )

            if isinstance(result, str):
                return {
                    "error": result,
                    "transactions": all_transactions,
                    "meta": {"pages_fetched": page - 1, "total_count": len(all_transactions)}
                }

            transactions = result.get("transactions", [])
            all_transactions.extend(transactions)

            meta = result.get("meta", {})
            total_pages = meta.get("total_pages", 1)

            page += 1

    except Exception as e:
        return {
            "error": str(e),
            "transactions": all_transactions,
            "meta": {"pages_fetched": page - 1, "total_count": len(all_transactions)}
        }

    return {
        "transactions": all_transactions,
        "meta": {"pages_fetched": page - 1, "total_count": len(all_transactions)}
    }
