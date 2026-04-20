"""
Configuration management for the Briq client.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


class Config:
    """Configuration class for the Briq client."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        env_path = Path(".") / ".env"
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)

        self._api_key: str | None = api_key or os.environ.get("BRIQ_API_KEY")
        self._base_url: str = base_url or os.environ.get("BRIQ_BASE_URL", "http://karibu.briq.tz")
        self._access_token: str | None = None

    @property
    def api_key(self) -> str | None:
        """Get the API key."""
        return self._api_key

    @api_key.setter
    def api_key(self, value: str | None) -> None:
        """Set the API key."""
        self._api_key = value

    @property
    def base_url(self) -> str:
        """Get the base URL."""
        return self._base_url

    @base_url.setter
    def base_url(self, value: str) -> None:
        """Set the base URL."""
        self._base_url = value

    @property
    def access_token(self) -> str | None:
        """Get the OAuth2 bearer access token."""
        return self._access_token

    @access_token.setter
    def access_token(self, value: str | None) -> None:
        """Set the OAuth2 bearer access token."""
        self._access_token = value

    @property
    def headers(self) -> dict[str, str]:
        """Get the headers for API requests."""
        if not self._api_key:
            raise ValueError(
                "API key not set. Set it using client.config.api_key = 'your_api_key' "
                "or by setting the BRIQ_API_KEY environment variable."
            )
        return {
            "X-API-Key": self._api_key,
            "Content-Type": "application/json",
        }
