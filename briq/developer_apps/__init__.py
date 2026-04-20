"""
Developer Apps module — Phase 2.
All routes under /developer-apps/... use OAuth2 Bearer auth.
Call client.login() before using these methods.
"""


class DeveloperAppsAPI:
    def __init__(self, client):
        self.client = client

    def list(self):
        """GET /developer-apps/ — list all developer apps for the authenticated user."""
        return self.client.get("developer-apps/", prefix="", auth="bearer")

    def create(self, app_name, app_description=None, workspace_id=None):
        """POST /developer-apps/ — create a new developer app."""
        data = {"app_name": app_name}
        if app_description is not None:
            data["app_description"] = app_description
        if workspace_id is not None:
            data["workspace_id"] = workspace_id
        return self.client.post("developer-apps/", data=data, prefix="", auth="bearer")

    def get(self, app_id):
        """GET /developer-apps/{app_id} — get a developer app by ID."""
        return self.client.get(f"developer-apps/{app_id}", prefix="", auth="bearer")

    def update(self, app_id, app_name=None, app_description=None, workspace_id=None):
        """PATCH /developer-apps/{app_id} — update a developer app."""
        data = {}
        if app_name is not None:
            data["app_name"] = app_name
        if app_description is not None:
            data["app_description"] = app_description
        if workspace_id is not None:
            data["workspace_id"] = workspace_id
        return self.client.patch(f"developer-apps/{app_id}", data=data, prefix="", auth="bearer")

    def delete(self, app_id):
        """DELETE /developer-apps/{app_id} — delete a developer app. Returns {} on 204."""
        return self.client.delete(f"developer-apps/{app_id}", prefix="", auth="bearer")

    def get_by_key(self, app_key):
        """GET /developer-apps/by-key/{app_key} — get a developer app by its app_key."""
        return self.client.get(f"developer-apps/by-key/{app_key}", prefix="", auth="bearer")

    def list_by_workspace(self, workspace_id):
        """GET /workspaces/{workspace_id}/developer-apps — list apps in a workspace."""
        return self.client.get(f"workspaces/{workspace_id}/developer-apps", prefix="", auth="bearer")

    def transfer(self, app_id, workspace_id):
        """POST /developer-apps/{app_id}/transfer — transfer app to another workspace."""
        return self.client.post(
            f"developer-apps/{app_id}/transfer",
            data={"workspace_id": workspace_id},
            prefix="",
            auth="bearer",
        )

    def attach_api_key(self, app_id, api_key_id):
        """POST /developer-apps/{app_id}/api-keys/{api_key_id}/attach — attach an API key."""
        return self.client.post(
            f"developer-apps/{app_id}/api-keys/{api_key_id}/attach",
            prefix="",
            auth="bearer",
        )

    def stats(self, app_id):
        """GET /developer-apps/{app_id}/stats — get API key statistics for an app."""
        return self.client.get(f"developer-apps/{app_id}/stats", prefix="", auth="bearer")

    def list_api_keys(self, app_id):
        """GET /developer-apps/{app_id}/api-keys — list all API keys for an app."""
        return self.client.get(f"developer-apps/{app_id}/api-keys", prefix="", auth="bearer")
