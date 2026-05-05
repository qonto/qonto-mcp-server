import base64
import io
import mimetypes
import os
import uuid
from typing import Optional
import requests
from requests.exceptions import RequestException
import qonto_mcp
from qonto_mcp import mcp

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "application/pdf"}

# Soft cap on inline base64 payloads. Qonto's per-attachment limit is 15 MB raw,
# which inflates to ~20 MB when base64-encoded; past that, JSON-RPC over stdio
# starts to struggle. Reject early with a clear error rather than failing later.
MAX_INLINE_BASE64_BYTES = 25 * 1024 * 1024


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
def upload_transaction_attachment(
    transaction_id: str,
    file_path: Optional[str] = None,
    file_content_base64: Optional[str] = None,
    filename: Optional[str] = None,
    mime_type: Optional[str] = None,
):
    """
    Uploads a file and attaches it to a Qonto transaction.

    Two input modes — provide exactly one of `file_path` or `file_content_base64`:

      1. file_path: path that the MCP server process can read.
         When the server runs in Docker, this must be a path INSIDE the
         container. Mount your host directory at run time, e.g.:
             docker run -v /Users/alice/receipts:/files:ro qonto-mcp-server
         and pass `file_path='/files/lunch.pdf'`.

      2. file_content_base64 + filename: base64-encoded bytes plus the original
         filename. Use this when the server has no shared filesystem with the
         client (Docker without a mount, remote server, etc.). `mime_type` is
         optional and inferred from `filename` if omitted. Soft size cap is
         ~25 MB encoded (≈18 MB raw); Qonto rejects raw files over 15 MB.

    Accepted file formats: JPEG, PNG, PDF.
    The attachment is processed asynchronously — it may not appear immediately
    when listing attachments.

    Args:
        transaction_id: UUID of the transaction to attach the file to
        file_path: Server-side path to the file (mutually exclusive with
            file_content_base64)
        file_content_base64: Base64-encoded file bytes (mutually exclusive
            with file_path)
        filename: Original filename — required when using file_content_base64;
            ignored when using file_path
        mime_type: Optional MIME-type override; inferred from the filename
            when absent

    Examples:
        # Path mode (server has access to the file):
        upload_transaction_attachment(
            transaction_id='aab86d8a-0d4c-4749-9a49-0ada88a9c423',
            file_path='/files/lunch.pdf',
        )

        # Inline mode (Docker without a mount, or remote server):
        upload_transaction_attachment(
            transaction_id='aab86d8a-0d4c-4749-9a49-0ada88a9c423',
            file_content_base64='JVBERi0xLjQK...',
            filename='lunch.pdf',
        )
    """
    # Exactly one input mode must be provided
    if (file_path is None) == (file_content_base64 is None):
        raise ValueError(
            "Provide exactly one of `file_path` or `file_content_base64`."
        )

    # Resolve the upload payload (filename, mime_type, file-like object factory)
    if file_path is not None:
        if not os.path.isfile(file_path):
            raise ValueError(
                f"File not found: {file_path}. "
                "If the MCP server runs in Docker, the path must exist INSIDE "
                "the container — mount the host directory with `-v` or use "
                "`file_content_base64` instead."
            )
        upload_filename = os.path.basename(file_path)
        resolved_mime = mime_type or mimetypes.guess_type(file_path)[0]

        def open_payload():
            return open(file_path, "rb")
    else:
        if not filename:
            raise ValueError(
                "`filename` is required when using `file_content_base64` "
                "(needed to derive the file extension and Qonto's stored name)."
            )
        try:
            content_bytes = base64.b64decode(file_content_base64, validate=True)
        except Exception as e:
            raise ValueError(f"Invalid base64 in `file_content_base64`: {e}")
        if len(content_bytes) > MAX_INLINE_BASE64_BYTES:
            raise ValueError(
                f"Decoded payload is {len(content_bytes)} bytes, which exceeds "
                f"the {MAX_INLINE_BASE64_BYTES}-byte soft cap. Use `file_path` "
                "with a mounted volume for files this large."
            )
        upload_filename = os.path.basename(filename)
        resolved_mime = mime_type or mimetypes.guess_type(upload_filename)[0]

        def open_payload():
            return io.BytesIO(content_bytes)

    if resolved_mime not in ALLOWED_MIME_TYPES:
        raise ValueError(
            f"Unsupported file type '{resolved_mime}'. "
            "Must be one of: JPEG, PNG, PDF."
        )

    url = f"{qonto_mcp.thirdparty_host}/v2/transactions/{transaction_id}/attachments"

    # Build upload headers — do NOT set Content-Type manually;
    # requests sets it with the correct multipart boundary automatically.
    # Add the required idempotency key on top of the global auth headers.
    upload_headers = {**qonto_mcp.headers, "X-Qonto-Idempotency-Key": str(uuid.uuid4())}
    upload_headers.pop("Accept", None)

    try:
        with open_payload() as f:
            response = requests.post(
                url,
                headers=upload_headers,
                files={"file": (upload_filename, f, resolved_mime)},
            )
        response.raise_for_status()
        # Response may be empty (async processing) or contain attachment id
        try:
            return response.json()
        except Exception:
            return {"status": "accepted", "message": "Attachment is being processed."}
    except RequestException as e:
        raise RuntimeError(f"Failed to upload attachment: {str(e)}")
