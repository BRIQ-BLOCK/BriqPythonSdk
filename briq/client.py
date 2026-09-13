"""
Client implementation for the Briq API.
"""

import requests

from .campaign import CampaignAPI
from .config import Config
from .developer_apps import DeveloperAppsAPI
from .email import EmailAPI
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

    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
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
        self.email = EmailAPI(self)

    def _build_url(self, endpoint: str, prefix: str = "v1") -> str:
        """Build the full URL for an API call.

        prefix="v1"  → {base_url}/v1/{endpoint}
        prefix=""    → {base_url}/{endpoint}   (root / developer-apps / meta paths)
        """
        base = self.config.base_url.rstrip("/")
        path = endpoint.lstrip("/")
        if prefix:
            return f"{base}/{prefix}/{path}"
        return f"{base}/{path}"

    def _user_agent(self) -> str:
        """Identify this SDK on the wire (not the default python-requests UA)."""
        from . import __version__

        return f"Briq-Python/{__version__}"

    def _build_headers(
        self,
        auth: str,
        extra_headers: dict[str, str] | None,
        files: dict | None,
    ) -> dict[str, str]:
        from .exceptions import BriqAuthError

        if auth == "bearer":
            if not self.config.access_token:
                raise BriqAuthError("Bearer token not set. Call client.login() first.")
            headers: dict[str, str] = {
                "Authorization": f"Bearer {self.config.access_token}",
                "Content-Type": "application/json",
            }
        elif auth == "api_key":
            headers = dict(self.config.headers)
        else:
            headers = {}

        if extra_headers:
            headers.update(extra_headers)

        headers.setdefault("User-Agent", self._user_agent())

        if files is not None:
            headers.pop("Content-Type", None)

        return headers

    def request(
        self,
        method: str,
        endpoint: str,
        data: dict | None = None,
        params: dict | None = None,
        prefix: str = "v1",
        auth: str = "api_key",
        extra_headers: dict[str, str] | None = None,
        files: dict | None = None,
    ) -> dict:
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
                    method=method,
                    url=url,
                    headers=headers,
                    files=files,
                    data=data,
                    params=params,
                )
            else:
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                    params=params,
                )

            body = self._parse_json(response)

            if 200 <= response.status_code < 300:
                if isinstance(body, dict) and body.get("success") is False and body.get("errors"):
                    raise BriqAPIError.from_envelope(body, response.status_code)
                if response.content:
                    return body  # type: ignore[return-value]
                return {}

            if response.status_code == 401:
                raise BriqAuthError("Authentication failed. Check your API key.")

            if isinstance(body, dict) and self._is_envelope_error(body):
                raise BriqAPIError.from_envelope(body, response.status_code)

            if response.status_code == 422:
                detail: list = []
                if isinstance(body, dict):
                    raw_detail = body.get("detail", [])
                    if isinstance(raw_detail, list):
                        detail = raw_detail
                    elif raw_detail:
                        detail = [raw_detail]
                raise BriqValidationError(f"Validation error: {detail}", detail=detail)

            if response.status_code == 400:
                error_data = body if body is not None else {"error": "Bad request"}
                raise BriqAPIError(
                    f"API error: {error_data}",
                    status_code=400,
                    body=error_data if isinstance(error_data, (dict, list)) else None,
                )

            raise BriqAPIError(
                f"API error: {response.status_code} {response.reason}",
                status_code=response.status_code,
                body=body if isinstance(body, (dict, list)) else None,
            )
        except (BriqAPIError, BriqAuthError, BriqValidationError):
            raise
        except requests.exceptions.RequestException as e:
            raise BriqRequestError(f"Request failed: {str(e)}")

    @staticmethod
    def _parse_json(response: requests.Response) -> dict | list | None:
        if not response.content:
            return None
        try:
            parsed = response.json()
        except ValueError:
            return None
        if isinstance(parsed, (dict, list)):
            return parsed
        return None

    @staticmethod
    def _is_envelope_error(body: dict) -> bool:
        errors = body.get("errors")
        if not isinstance(errors, list) or not errors:
            return False
        first = errors[0]
        return isinstance(first, dict) and "code" in first

    def login(self, username: str, password: str) -> dict:
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
            token_data: dict = response.json()
            self.config.access_token = token_data["access_token"]
            return token_data
        except requests.exceptions.HTTPError:
            raise BriqAuthError("Login failed. Check your credentials.")
        except requests.exceptions.RequestException as e:
            raise BriqRequestError(f"Login request failed: {str(e)}")

    def get(
        self,
        endpoint: str,
        params: dict | None = None,
        prefix: str = "v1",
        auth: str = "api_key",
        extra_headers: dict[str, str] | None = None,
    ) -> dict:
        return self.request(
            "GET", endpoint, params=params, prefix=prefix, auth=auth, extra_headers=extra_headers
        )

    def post(
        self,
        endpoint: str,
        data: dict | None = None,
        prefix: str = "v1",
        auth: str = "api_key",
        extra_headers: dict[str, str] | None = None,
        files: dict | None = None,
    ) -> dict:
        return self.request(
            "POST",
            endpoint,
            data=data,
            prefix=prefix,
            auth=auth,
            extra_headers=extra_headers,
            files=files,
        )

    def patch(
        self,
        endpoint: str,
        data: dict | None = None,
        prefix: str = "v1",
        auth: str = "api_key",
        extra_headers: dict[str, str] | None = None,
    ) -> dict:
        return self.request(
            "PATCH", endpoint, data=data, prefix=prefix, auth=auth, extra_headers=extra_headers
        )

    def delete(
        self,
        endpoint: str,
        prefix: str = "v1",
        auth: str = "api_key",
        extra_headers: dict[str, str] | None = None,
    ) -> dict:
        return self.request(
            "DELETE", endpoint, prefix=prefix, auth=auth, extra_headers=extra_headers
        )

    def set_api_key(self, api_key: str) -> None:
        self.config.api_key = api_key
