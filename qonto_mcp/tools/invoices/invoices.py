import requests
from datetime import datetime
from typing import Dict, Optional
from requests.exceptions import RequestException

import qonto_mcp
from qonto_mcp import mcp


@mcp.tool()
def get_client_invoices(
    current_page: Optional[int] = None,
    per_page: Optional[int] = None,
    status: Optional[str] = None,
    updated_at_from: Optional[datetime] = None,
    updated_at_to: Optional[datetime] = None,
) -> Dict:
    """
    Get client invoices from Qonto API.

    Args:
        current_page: The current page of results to retrieve.
        per_page: The number of results per page.
        status: Filter invoices by status.
        updated_at_from: Filter invoices updated from this date.
        updated_at_to: Filter invoices updated until this date.

    Example: get_client_invoices(per_page=10, status="paid")
    """
    url = f"{qonto_mcp.thirdparty_host}/v2/client_invoices"
    params = {}
    if current_page is not None:
        params["page"] = current_page
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
        raise RuntimeError(f"Failed to fetch client invoices {str(e)}")


@mcp.tool()
def get_supplier_invoices(
    current_page: Optional[int] = None,
    per_page: Optional[int] = None,
    status: Optional[str] = None,
    updated_at_from: Optional[datetime] = None,
    updated_at_to: Optional[datetime] = None,
) -> Dict:
    """
    Get supplier invoices from Qonto API.

    Args:
        current_page: The current page of results to retrieve.
        per_page: The number of results per page.
        status: Filter invoices by status.
        updated_at_from: Filter invoices updated from this date.
        updated_at_to: Filter invoices updated until this date.

    Example: get_supplier_invoices(per_page=10, status="pending")
    """
    url = f"{qonto_mcp.thirdparty_host}/v2/supplier_invoices"
    params = {}
    if current_page is not None:
        params["page"] = current_page
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
        raise RuntimeError(f"Failed to fetch supplier invoices {str(e)}")


@mcp.tool()
def get_credit_notes(
    current_page: Optional[int] = None,
    per_page: Optional[int] = None,
    updated_at_from: Optional[datetime] = None,
    updated_at_to: Optional[datetime] = None,
) -> Dict:
    """
    Get credit notes from Qonto API.

    Args:
        current_page: The current page of results to retrieve.
        per_page: The number of results per page.
        updated_at_from: Filter credit notes updated from this date.
        updated_at_to: Filter credit notes updated until this date.

    Example: get_credit_notes(per_page=5)
    """
    url = f"{qonto_mcp.thirdparty_host}/v2/credit_notes"
    params = {}
    if current_page is not None:
        params["page"] = current_page
    if per_page is not None:
        params["per_page"] = per_page
    if updated_at_from is not None:
        params["updated_at_from"] = updated_at_from.isoformat()
    if updated_at_to is not None:
        params["updated_at_to"] = updated_at_to.isoformat()

    try:
        response = requests.get(url, headers=qonto_mcp.headers, params=params)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        raise RuntimeError(f"Failed to fetch credit notes {str(e)}")
