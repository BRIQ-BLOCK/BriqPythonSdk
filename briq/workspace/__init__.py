"""
Workspace management module for the Briq API — Phase 3.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import Client


class WorkspaceAPI:
    """
    Workspace management API for Briq.

    Provides methods for creating, listing, retrieving, and updating workspaces.
    """

    def __init__(self, client: Client) -> None:
        self.client = client

    def create(self, name: str, description: str | None = None, developer_access: bool = False) -> dict:
        """
        Create a new workspace.

        Args:
            name (str): Name of the workspace
            description (str, optional): Description of the workspace
            developer_access (bool): Whether to enable developer access (default False)

        Returns:
            dict: Created workspace data
        """
        data: dict = {"name": name, "developer_access": developer_access}
        if description is not None:
            data["description"] = description
        return self.client.post("workspace/create/", data=data)

    def list(self) -> dict:
        """List all workspaces."""
        return self.client.get("workspace/all/")

    def get(self, workspace_id: str) -> dict:
        """Get a workspace by ID."""
        return self.client.get(f"workspace/{workspace_id}")

    def update(
        self,
        workspace_id: str,
        name: str | None = None,
        description: str | None = None,
        developer_access: bool | None = None,
    ) -> dict:
        """
        Update a workspace.

        Args:
            workspace_id (str): ID of the workspace to update
            name (str, optional): New name for the workspace
            description (str, optional): New description for the workspace
            developer_access (bool, optional): Update developer access flag

        Returns:
            dict: Updated workspace data
        """
        data: dict = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if developer_access is not None:
            data["developer_access"] = developer_access
        return self.client.patch(f"workspace/update/{workspace_id}", data=data)
