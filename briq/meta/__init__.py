"""
Meta / Developer info module — Phase 1.
Covers: GET /, GET /version, GET /karibu/x-api-key
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import Client


class MetaAPI:
    """Meta and developer info API for Briq."""

    def __init__(self, client: Client) -> None:
        self.client = client

    def hello(self) -> dict:
        """GET / — redirect to Briq landing page info."""
        return self.client.get("", prefix="", auth="none")

    def get_version(self) -> dict:
        """GET /version — return API version and deployment information."""
        return self.client.get("version", prefix="", auth="none")

    def developer_stats(self) -> dict:
        """GET /karibu/x-api-key — verify API key and return developer information."""
        return self.client.get("karibu/x-api-key", prefix="", auth="api_key")
