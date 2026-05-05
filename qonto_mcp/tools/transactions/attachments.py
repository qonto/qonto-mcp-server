import os
import uuid
import mimetypes
from typing import Optional
import requests
from requests.exceptions import RequestException
import qonto_mcp
from qonto_mcp import mcp

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "application/pdf"}


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
def upload_transaction_attachment(transaction_id: str, file_path: str):
    """
    Uploads a file from the local filesystem and attaches it to a Qonto transaction.

    Accepted file formats: JPEG, PNG, PDF.
    The attachment is processed asynchronously — it may not appear immediately when
    listing attachments.

    Args:
        transaction_id: UUID of the transaction to attach the file to
        file_path: Absolute or relative path to the file on disk (JPEG/PNG/PDF)

    Example: upload_transaction_attachment(
                transaction_id='aab86d8a-0d4c-4749-9a49-0ada88a9c423',
                file_path='/Users/alice/receipts/lunch.pdf'
             )
    """
    # Validate file exists
    if not os.path.isfile(file_path):
        raise ValueError(f"File not found: {file_path}")

    # Detect and validate MIME type
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type not in ALLOWED_MIME_TYPES:
        raise ValueError(
            f"Unsupported file type '{mime_type}'. Must be one of: JPEG, PNG, PDF."
        )

    url = f"{qonto_mcp.thirdparty_host}/v2/transactions/{transaction_id}/attachments"
    filename = os.path.basename(file_path)

    # Build upload headers — do NOT set Content-Type manually;
    # requests sets it with the correct multipart boundary automatically.
    # Add the required idempotency key on top of the global auth headers.
    upload_headers = {**qonto_mcp.headers, "X-Qonto-Idempotency-Key": str(uuid.uuid4())}
    upload_headers.pop("Accept", None)

    try:
        with open(file_path, "rb") as f:
            response = requests.post(
                url,
                headers=upload_headers,
                files={"file": (filename, f, mime_type)},
            )
        response.raise_for_status()
        # Response may be empty (async processing) or contain attachment id
        try:
            return response.json()
        except Exception:
            return {"status": "accepted", "message": "Attachment is being processed."}
    except RequestException as e:
        raise RuntimeError(f"Failed to upload attachment: {str(e)}")
