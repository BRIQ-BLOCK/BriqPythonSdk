"""
Message management module for the Briq API — Phase 4.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import Client


class MessageAPI:
    """
    Message management API for Briq.

    Provides methods for sending messages and retrieving message history and logs.
    """

    def __init__(self, client: Client) -> None:
        self.client = client

    def send_instant(
        self,
        content: str,
        recipients: list[str],
        sender_id: str,
        campaign_id: str | None = None,
        groups: list[str] | None = None,
        flash: bool = False,
        send_at: str | None = None,
        app_id: str | None = None,
    ) -> dict:
        """
        Send an instant message to one or multiple recipients.

        Args:
            content (str): Message content
            recipients (list[str]): List of recipient phone numbers
            sender_id (str): Registered sender ID name
            campaign_id (str, optional): Campaign ID to associate the message with
            groups (list[str], optional): Group IDs to also send to
            flash (bool): Send as a flash message (default False)
            send_at (str, optional): ISO 8601 UTC datetime to schedule the message
                                     (e.g. "2025-12-11T15:30:00Z")
            app_id (str, optional): Developer app ID for webhook notifications (X-App-ID header)

        Returns:
            dict: SendInstantMessageResponse with job_id, status, message, stats, meta
        """
        data = {
            "content": content,
            "recipients": recipients,
            "sender_id": sender_id,
            "flash": flash,
        }
        if campaign_id is not None:
            data["campaign_id"] = campaign_id
        if groups is not None:
            data["groups"] = groups
        if send_at is not None:
            data["send_at"] = send_at

        extra_headers = {"X-App-ID": app_id} if app_id else None
        return self.client.post("message/send-instant", data=data, extra_headers=extra_headers)

    def send_campaign(
        self,
        campaign_id: str,
        content: str,
        sender_id: str,
        start_date: str | None = None,
        end_date: str | None = None,
        frequency: str | None = None,
        app_id: str | None = None,
    ) -> dict:
        """
        Send a message to all contacts in a campaign.

        Args:
            campaign_id (str): ID of the campaign
            content (str): Message content
            sender_id (str): Registered sender ID name (2–13 characters)
            start_date (str, optional): ISO 8601 datetime for when sending starts
            end_date (str, optional): ISO 8601 datetime for when sending ends
            frequency (str, optional): One of once, hourly, daily, weekly, monthly (default once)
            app_id (str, optional): Developer app ID for webhook notifications (X-App-ID header)

        Returns:
            dict: Response data
        """
        data = {
            "campaign_id": campaign_id,
            "content": content,
            "sender_id": sender_id,
        }
        if start_date is not None:
            data["start_date"] = start_date
        if end_date is not None:
            data["end_date"] = end_date
        if frequency is not None:
            data["frequency"] = frequency

        extra_headers = {"X-App-ID": app_id} if app_id else None
        return self.client.post("message/send-campaign", data=data, extra_headers=extra_headers)

    def get_logs(self) -> dict:
        """GET /v1/message/logs — fetch all message logs for the authenticated user."""
        return self.client.get("message/logs")

    def get_history(self) -> dict:
        """GET /v1/message/history — retrieve all messages sent by the authenticated user."""
        return self.client.get("message/history")

    def get_history_by_recipient(self, recipient: str) -> dict:
        """
        GET /v1/message/history/recipient/{recipient} — messages sent to a specific recipient.

        Args:
            recipient (str): Recipient phone number

        Returns:
            dict: List of MessageResponseRaw objects
        """
        return self.client.get(f"message/history/recipient/{recipient}")

    def get_message_log(self, message_id: str) -> dict:
        """
        GET /v1/message/message-log/{message_id} — retrieve details of a specific message.

        Args:
            message_id (str): Message ID

        Returns:
            dict: MessageResponseRaw object
        """
        return self.client.get(f"message/message-log/{message_id}")
