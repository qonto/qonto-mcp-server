from datetime import datetime

import pytest
from requests.exceptions import RequestException

from qonto_mcp.tools.invoices.invoices import get_client_invoices


def test_only_the_provided_filters_are_sent(configured, capture_get):
    get_client_invoices(per_page=10, status="paid")

    params = capture_get.calls[0]["params"]
    assert params["per_page"] == 10
    assert params["status"] == "paid"
    assert "updated_at_from" not in params
    assert "updated_at_to" not in params


def test_dates_are_sent_in_iso_format(configured, capture_get):
    get_client_invoices(updated_at_from=datetime(2026, 1, 2, 3, 4, 5))

    assert capture_get.calls[0]["params"]["updated_at_from"] == "2026-01-02T03:04:05"


def test_request_failures_are_raised_as_runtime_errors(configured, capture_get):
    capture_get.set_error(RequestException("connection reset"))

    with pytest.raises(RuntimeError, match="Failed to fetch client invoices"):
        get_client_invoices()
