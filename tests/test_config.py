import pytest

import qonto_mcp


@pytest.mark.parametrize(
    "missing",
    ["QONTO_THIRDPARTY_HOST", "QONTO_API_KEY", "QONTO_ORGANIZATION_ID"],
)
def test_setup_requires_every_mandatory_variable(qonto_env, monkeypatch, missing):
    monkeypatch.delenv(missing, raising=False)

    with pytest.raises(ValueError, match=missing):
        qonto_mcp.setup_qonto_config()


def test_setup_builds_the_authorization_header(configured):
    assert configured.headers["Accept"] == "application/json"
    assert configured.headers["Authorization"] == "test-org:test-api-key"
    assert configured.thirdparty_host == "https://thirdparty.example.com"


def test_staging_token_is_optional(configured):
    assert "X-Qonto-Staging-Token" not in configured.headers


def test_staging_token_is_forwarded_when_set(qonto_env, monkeypatch):
    monkeypatch.setenv("QONTO_STAGING_TOKEN", "staging-token")

    qonto_mcp.setup_qonto_config()

    assert qonto_mcp.headers["X-Qonto-Staging-Token"] == "staging-token"
