import requests
from typing import Dict, Optional
import qonto_mcp
from qonto_mcp import mcp


def apply_qonto_transaction_data_filter(params: Dict[str, object], data_filter: Optional[Dict[str, str]]) -> None:
    if data_filter is None:
        return

    field = data_filter.get("field")

    if field not in {"updated_at", "emitted_at", "settled_at"}:
        raise ValueError("data_filter.field must be one of: updated_at, emitted_at, settled_at")

    from_value = data_filter.get("from")
    to_value = data_filter.get("to")

    if from_value is None and to_value is None:
        raise ValueError("data_filter must include at least one of: from, to")

    if from_value is not None:
        params[f"{field}_from"] = from_value

    if to_value is not None:
        params[f"{field}_to"] = to_value


@mcp.tool()
def get_qonto_transactions(
    bank_account_id: str,
    page: Optional[int] = None,
    per_page: Optional[int] = None,
    data_filter: Optional[Dict[str, str]] = None,
    sort_by: Optional[str] = None,
):
    """
    Retrieves transactions from the Qonto API for a specific bank account with optional
    pagination, date filtering, and sorting.

    Args:
        bank_account_id: UUID of the bank account to retrieve transactions for
        page: Page number to retrieve
        per_page: Number of transactions per page
        data_filter: Optional date filter object with:
                     field: updated_at, emitted_at, or settled_at
                     from: ISO 8601 lower bound
                     to: ISO 8601 upper bound
        sort_by: Qonto sort expression, for example updated_at:desc

    Example: get_qonto_transactions(
                bank_account_id='0193f298-d9f3-7b77-8566-ce356449d7f3',
                page=1,
                per_page=25,
                data_filter={
                    'field': 'updated_at',
                    'from': '2025-01-01T00:00:00Z'
                },
                sort_by='updated_at:desc'
             )
    """
    url = f"{qonto_mcp.thirdparty_host}/v2/transactions"
    params: Dict[str, object] = {"bank_account_id": bank_account_id}

    if page is not None:
        params["current_page"] = page

    if per_page is not None:
        params["per_page"] = per_page

    apply_qonto_transaction_data_filter(params, data_filter)

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
