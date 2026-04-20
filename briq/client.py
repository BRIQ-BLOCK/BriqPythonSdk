"""
Client implementation for the Briq API.
"""

import requests

from .campaign import CampaignAPI
from .config import Config
from .developer_apps import DeveloperAppsAPI
from .message import MessageAPI
from .meta import MetaAPI
from .otp import OtpAPI
from .voice import VoiceAPI
from .webhooks import WebhooksAPI
from .workspace import WorkspaceAPI


class Client:
    """
    Main client class for interacting with the Briq API.

    Provides access to all API endpoints through dedicated modules.
    """

    def __init__(self, api_key=None, base_url=None):
        self.config = Config(api_key=api_key, base_url=base_url)
        self.session = requests.Session()

        self.workspace = WorkspaceAPI(self)
        self.campaign = CampaignAPI(self)
        self.message = MessageAPI(self)
        self.meta = MetaAPI(self)
        self.developer_apps = DeveloperAppsAPI(self)
        self.otp = OtpAPI(self)
        self.voice = VoiceAPI(self)
        self.webhooks = WebhooksAPI(self)

    def _build_url(self, endpoint, prefix="v1"):
        """Build the full URL for an API call.

        prefix="v1"  → {base_url}/v1/{endpoint}
        prefix=""    → {base_url}/{endpoint}   (root / developer-apps / meta paths)
        """
        base = self.config.base_url.rstrip("/")
        path = endpoint.lstrip("/")
        if prefix:
            return f"{base}/{prefix}/{path}"
        return f"{base}/{path}"

    def _build_headers(self, auth, extra_headers, files):
        from .exceptions import BriqAuthError
        if auth == "bearer":
            if not self.config.access_token:
                raise BriqAuthError("Bearer token not set. Call client.login() first.")
            headers = {
                "Authorization": f"Bearer {self.config.access_token}",
                "Content-Type": "application/json",
            }
        elif auth == "api_key":
            headers = dict(self.config.headers)
        else:
            headers = {}

        if extra_headers:
            headers.update(extra_headers)

        if files is not None:
            headers.pop("Content-Type", None)

        return headers

    def request(self, method, endpoint, data=None, params=None,
                prefix="v1", auth="api_key", extra_headers=None, files=None):
        """
        Make a request to the Briq API.

        Args:
            method (str): HTTP method (GET, POST, PATCH, DELETE, etc.)
            endpoint (str): API endpoint path (relative to prefix)
            data (dict, optional): JSON request body
            params (dict, optional): Query parameters
            prefix (str): URL prefix — "v1" (default) or "" for root/developer paths
            auth (str): Auth mode — "api_key" (default), "bearer", or "none"
            extra_headers (dict, optional): Additional headers merged into the request
            files (dict, optional): Files for multipart/form-data upload

        Returns:
            dict: Response data (empty dict for no-body responses such as 204)

        Raises:
            BriqAuthError: 401 authentication failure
            BriqValidationError: 422 validation failure
            BriqAPIError: Other HTTP error
            BriqRequestError: Network / transport failure
        """
        from .exceptions import BriqAPIError, BriqAuthError, BriqRequestError, BriqValidationError

        url = self._build_url(endpoint, prefix=prefix)
        headers = self._build_headers(auth, extra_headers, files)

        try:
            if files is not None:
                response = self.session.request(
                    method=method, url=url, headers=headers,
                    files=files, data=data, params=params,
                )
            else:
                response = self.session.request(
                    method=method, url=url, headers=headers,
                    json=data, params=params,
                )

            response.raise_for_status()

            if response.content:
                return response.json()
            return {}

        except requests.exceptions.HTTPError as e:
            status = response.status_code
            if status == 401:
                raise BriqAuthError("Authentication failed. Check your API key.")
            elif status == 422:
                detail = []
                try:
                    detail = response.json().get("detail", [])
                except Exception:
                    pass
                raise BriqValidationError(f"Validation error: {detail}", detail=detail)
            elif status == 400:
                error_data = response.json() if response.content else {"error": "Bad request"}
                raise BriqAPIError(f"API error: {error_data}")
            else:
                raise BriqAPIError(f"API error: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise BriqRequestError(f"Request failed: {str(e)}")

    def login(self, username, password):
        """
        Authenticate with OAuth2 password flow and store the bearer token.

        Required before calling Developer Apps endpoints.

        Args:
            username (str): Account username / email
            password (str): Account password

        Returns:
            dict: Token response (includes access_token, token_type)
        """
        from .exceptions import BriqAuthError, BriqRequestError
        url = f"{self.config.base_url.rstrip('/')}/auth/login"
        try:
            response = self.session.post(
                url,
                data={"username": username, "password": password, "grant_type": "password"},
            )
            response.raise_for_status()
            token_data = response.json()
            self.config.access_token = token_data["access_token"]
            return token_data
        except requests.exceptions.HTTPError:
            raise BriqAuthError("Login failed. Check your credentials.")
        except requests.exceptions.RequestException as e:
            raise BriqRequestError(f"Login request failed: {str(e)}")

    def get(self, endpoint, params=None, prefix="v1", auth="api_key", extra_headers=None):
        return self.request("GET", endpoint, params=params, prefix=prefix, auth=auth, extra_headers=extra_headers)

    def post(self, endpoint, data=None, prefix="v1", auth="api_key", extra_headers=None, files=None):
        return self.request("POST", endpoint, data=data, prefix=prefix, auth=auth, extra_headers=extra_headers, files=files)

    def patch(self, endpoint, data=None, prefix="v1", auth="api_key", extra_headers=None):
        return self.request("PATCH", endpoint, data=data, prefix=prefix, auth=auth, extra_headers=extra_headers)

    def delete(self, endpoint, prefix="v1", auth="api_key", extra_headers=None):
        return self.request("DELETE", endpoint, prefix=prefix, auth=auth, extra_headers=extra_headers)

    def set_api_key(self, api_key):
        self.config.api_key = api_key
