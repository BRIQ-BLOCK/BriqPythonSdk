"""
Campaign management module for the Briq API.
"""


class CampaignAPI:
    """Campaign management API for Briq."""

    def __init__(self, client):
        self.client = client

    def create(self, workspace_id, name, description=None, launch_date=None):
        """Create a new campaign."""
        data = {"workspace_id": workspace_id, "name": name}
        if description:
            data["description"] = description
        if launch_date:
            data["launch_date"] = launch_date
        return self.client.post("campaign/create/", data=data)

    def list(self):
        """List all campaigns."""
        return self.client.get("campaign/all/")

    def get(self, campaign_id):
        """Get a campaign by ID."""
        return self.client.get(f"campaign/{campaign_id}/")

    def update(self, campaign_id, name=None, description=None, launch_date=None):
        """Update a campaign."""
        data = {}
        if name:
            data["name"] = name
        if description:
            data["description"] = description
        if launch_date:
            data["launch_date"] = launch_date
        return self.client.patch(f"campaign/update/{campaign_id}", data=data)
