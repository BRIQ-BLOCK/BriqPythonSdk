"""
Webhooks module for the Briq API — Phase 7.
All routes under /v1/webhooks/
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import Client


class WebhooksAPI:
    """
    Webhooks API for Briq.

    Manage webhooks for developer apps. Supported service types: sms, voice, otp, whatsapp, email.
    Note: secret_token in responses may be masked.
    """

    def __init__(self, client: Client) -> None:
        self.client = client

    def create(
        self,
        app_id: str,
        service_type: str,
        url: str,
        secret_token: str | None = None,
    ) -> dict:
        """
        POST /v1/webhooks/ — create a new webhook for a developer app.

        Args:
            app_id (str): UUID of the developer app
            service_type (str): One of sms, voice, otp, whatsapp, email
            url (str): URL where webhook events will be sent
            secret_token (str, optional): Secret for signing outgoing requests (min 16 chars)

        Returns:
            dict: WebhookOut
        """
        data = {"app_id": app_id, "service_type": service_type, "url": url}
        if secret_token is not None:
            data["secret_token"] = secret_token
        return self.client.post("webhooks/", data=data)

    def list(self) -> dict:
        """GET /v1/webhooks/all — list all webhooks for the authenticated user."""
        return self.client.get("webhooks/all")

    def list_by_app(self, app_id: str) -> dict:
        """GET /v1/webhooks/app/{app_id} — list all webhooks for a specific developer app."""
        return self.client.get(f"webhooks/app/{app_id}")

    def get(self, webhook_id: str) -> dict:
        """GET /v1/webhooks/{webhook_id} — get a specific webhook by ID."""
        return self.client.get(f"webhooks/{webhook_id}")

    def update(
        self,
        webhook_id: str,
        service_type: str | None = None,
        url: str | None = None,
        secret_token: str | None = None,
    ) -> dict:
        """
        PATCH /v1/webhooks/{webhook_id} — update a webhook's configuration.

        Args:
            webhook_id (str): ID of the webhook to update
            service_type (str, optional): New service type
            url (str, optional): New webhook URL
            secret_token (str, optional): New secret token (min 16 chars)

        Returns:
            dict: WebhookOut
        """
        data = {}
        if service_type is not None:
            data["service_type"] = service_type
        if url is not None:
            data["url"] = url
        if secret_token is not None:
            data["secret_token"] = secret_token
        return self.client.patch(f"webhooks/{webhook_id}", data=data)

    def delete(self, webhook_id: str) -> dict:
        """DELETE /v1/webhooks/{webhook_id} — delete a webhook. Returns {} on 204."""
        return self.client.delete(f"webhooks/{webhook_id}")
