import mimetypes
import os
import uuid
import requests
from datetime import datetime
from typing import Dict, Optional
from requests.exceptions import RequestException

import qonto_mcp
from qonto_mcp import mcp


_SUPPLIER_INVOICE_MIME_TYPES = {"image/jpeg", "image/png", "application/pdf"}


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
        params["current_page"] = current_page
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


@mcp.tool()
def create_qonto_supplier_invoice(
    file_path: Optional[str] = None,
    attachment_id: Optional[str] = None,
) -> Dict:
    """
    Create a supplier invoice in Qonto from a local file or an existing attachment.

    Submits one supplier invoice (vendor bill) to Qonto's bulk endpoint. Qonto
    will OCR the document and route it through the standard supplier-invoice
    approval workflow. Use this to record paid expenses, vendor receipts, or
    pay-by-invoice items.

    Provide exactly one of:
        - file_path: a local PDF/PNG/JPEG to upload, OR
        - attachment_id: the UUID of an attachment already known to Qonto
          (e.g. one returned by list_qonto_transaction_attachments).

    The endpoint always returns HTTP 200 — even when an individual item fails.
    Inspect the `errors` array of the returned object to confirm success.

    Args:
        file_path: Absolute or relative path to a PDF/JPEG/PNG file on disk.
        attachment_id: UUID of an existing Qonto attachment to convert into
            a supplier invoice.

    Example: create_qonto_supplier_invoice(file_path="/Users/alice/bills/acme.pdf")
    """
    if (file_path is None) == (attachment_id is None):
        raise ValueError(
            "Provide exactly one of file_path or attachment_id (not both, not neither)."
        )

    url = f"{qonto_mcp.thirdparty_host}/v2/supplier_invoices/bulk"
    idempotency_key = str(uuid.uuid4())

    upload_headers = {**qonto_mcp.headers}
    upload_headers.pop("Accept", None)

    try:
        if file_path is not None:
            if not os.path.isfile(file_path):
                raise ValueError(f"File not found: {file_path}")
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type not in _SUPPLIER_INVOICE_MIME_TYPES:
                raise ValueError(
                    f"Unsupported file type '{mime_type}'. Must be PDF, JPEG, or PNG."
                )
            filename = os.path.basename(file_path)
            with open(file_path, "rb") as f:
                files = {
                    "supplier_invoices[][file]": (filename, f, mime_type),
                    "supplier_invoices[][idempotency_key]": (None, idempotency_key),
                }
                response = requests.post(url, headers=upload_headers, files=files)
        else:
            files = {
                "supplier_invoices[][attachment_id]": (None, attachment_id),
                "supplier_invoices[][idempotency_key]": (None, idempotency_key),
            }
            response = requests.post(url, headers=upload_headers, files=files)

        response.raise_for_status()
        return response.json()
    except RequestException as e:
        raise RuntimeError(f"Failed to create supplier invoice: {str(e)}")
