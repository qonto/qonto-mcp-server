import requests
from requests.exceptions import RequestException
import qonto_mcp
from qonto_mcp import mcp


@mcp.tool()
def get_qonto_organization(include_external_accounts: bool = True):
    """
    Retrieves organization and list of bank accounts from the Qonto API.

    By default, includes both Qonto accounts and external accounts connected
    to the organization (e.g. accounts aggregated via open banking). Each
    bank account in the response carries an `is_external_account` flag so
    callers can filter as needed. Pass `include_external_accounts=False` to
    restrict the response to Qonto-native accounts only.

    Example: get_qonto_organization()
    Example: get_qonto_organization(include_external_accounts=False)
    """
    url = f"{qonto_mcp.thirdparty_host}/v2/organization"
    params = {"include_external_accounts": str(include_external_accounts).lower()}

    try:
        response = requests.get(url, headers=qonto_mcp.headers, params=params)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        raise RuntimeError(f"Error fetching Qonto organization {str(e)}")
