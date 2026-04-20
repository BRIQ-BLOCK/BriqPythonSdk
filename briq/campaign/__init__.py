"""
Campaign management module for the Briq API.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import Client


class CampaignAPI:
    """Campaign management API for Briq."""

    def __init__(self, client: Client) -> None:
        self.client = client

    def create(
        self,
        workspace_id: str,
        name: str,
        description: str | None = None,
        launch_date: str | None = None,
    ) -> dict:
        """
        Create a new campaign.

        Args:
            workspace_id (str): ID of the workspace to create the campaign in
            name (str): Name of the campaign
            description (str, optional): Description of the campaign
            launch_date (str, optional): ISO 8601 datetime for the campaign launch

        Returns:
            dict: Created campaign data
        """
        data: dict = {"workspace_id": workspace_id, "name": name}
        if description:
            data["description"] = description
        if launch_date:
            data["launch_date"] = launch_date
        return self.client.post("campaign/create/", data=data)

    def list(self) -> dict:
        """List all campaigns."""
        return self.client.get("campaign/all/")

    def get(self, campaign_id: str) -> dict:
        """Get a campaign by ID."""
        return self.client.get(f"campaign/{campaign_id}/")

    def update(
        self,
        campaign_id: str,
        name: str | None = None,
        description: str | None = None,
        launch_date: str | None = None,
    ) -> dict:
        """
        Update a campaign.

        Args:
            campaign_id (str): ID of the campaign to update
            name (str, optional): New name for the campaign
            description (str, optional): New description
            launch_date (str, optional): New ISO 8601 launch datetime

        Returns:
            dict: Updated campaign data
        """
        data: dict = {}
        if name:
            data["name"] = name
        if description:
            data["description"] = description
        if launch_date:
            data["launch_date"] = launch_date
        return self.client.patch(f"campaign/update/{campaign_id}", data=data)
