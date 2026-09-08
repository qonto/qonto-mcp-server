from qonto_mcp.tools.transactions.transactions import (
    get_qonto_transaction,
    get_qonto_transactions,
)


def test_transactions_are_scoped_to_a_bank_account(configured, capture_get):
    capture_get.set_payload({"transactions": []})

    result = get_qonto_transactions(bank_account_id="account-1")

    call = capture_get.calls[0]
    assert call["url"] == "https://thirdparty.example.com/v2/transactions"
    assert call["params"] == {"bank_account_id": "account-1"}
    assert call["headers"]["Authorization"] == "test-org:test-api-key"
    assert result == {"transactions": []}


def test_includes_are_sent_as_a_repeated_parameter(configured, capture_get):
    get_qonto_transaction(transaction_id="tx-1", includes=["labels", "attachments"])

    call = capture_get.calls[0]
    assert call["url"] == "https://thirdparty.example.com/v2/transactions/tx-1"
    assert call["params"] == {"includes[]": ["labels", "attachments"]}


def test_transaction_without_includes_sends_no_parameters(configured, capture_get):
    get_qonto_transaction(transaction_id="tx-1")

    assert capture_get.calls[0]["params"] == {}


def test_transaction_errors_are_returned_as_a_message(configured, capture_get):
    capture_get.set_error(RuntimeError("boom"))

    result = get_qonto_transactions(bank_account_id="account-1")

    assert result == "Error fetching Qonto transactions: boom"
