import pytest

import qonto_mcp

ENV = {
    "QONTO_THIRDPARTY_HOST": "https://thirdparty.example.com",
    "QONTO_API_KEY": "test-api-key",
    "QONTO_ORGANIZATION_ID": "test-org",
}


@pytest.fixture
def qonto_env(monkeypatch):
    """Set the environment variables the server requires, and nothing else."""
    for name, value in ENV.items():
        monkeypatch.setenv(name, value)
    monkeypatch.delenv("QONTO_STAGING_TOKEN", raising=False)
    return dict(ENV)


@pytest.fixture
def configured(qonto_env):
    """Configure the module globals the tools read at call time."""
    qonto_mcp.setup_qonto_config()
    return qonto_mcp


class FakeResponse:
    """Minimal stand-in for requests.Response."""

    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


@pytest.fixture
def capture_get(monkeypatch):
    """Replace requests.get, record the call, and return a canned response.

    Use `set_payload` for the happy path and `set_error` to make the request
    raise, so a test never reaches the network.
    """

    calls = []

    def fake_get(url, headers=None, params=None, **kwargs):
        calls.append({"url": url, "headers": headers, "params": params})
        if fake_get.error is not None:
            raise fake_get.error
        return FakeResponse(fake_get.payload)

    fake_get.calls = calls
    fake_get.payload = {}
    fake_get.error = None
    fake_get.set_payload = lambda payload: setattr(fake_get, "payload", payload)
    fake_get.set_error = lambda error: setattr(fake_get, "error", error)

    monkeypatch.setattr("requests.get", fake_get)
    return fake_get
