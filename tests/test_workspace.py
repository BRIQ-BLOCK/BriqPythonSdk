import os
import sys
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from briq.workspace import WorkspaceAPI


class TestWorkspaceAPI(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        self.workspace_api = WorkspaceAPI(self.mock_client)

    def test_init(self):
        self.assertIsNotNone(self.workspace_api)
        self.assertEqual(self.workspace_api.client, self.mock_client)

    def test_create_name_only(self):
        self.workspace_api.create("Test Workspace")
        self.mock_client.post.assert_called_once_with(
            "workspace/create/",
            data={"name": "Test Workspace", "developer_access": False},
        )

    def test_create_with_description(self):
        self.workspace_api.create("Test Workspace", description="Test Description")
        self.mock_client.post.assert_called_once_with(
            "workspace/create/",
            data={"name": "Test Workspace", "developer_access": False, "description": "Test Description"},
        )

    def test_create_with_developer_access(self):
        self.workspace_api.create("Dev Workspace", developer_access=True)
        self.mock_client.post.assert_called_once_with(
            "workspace/create/",
            data={"name": "Dev Workspace", "developer_access": True},
        )

    def test_list(self):
        mock_response = [
            {"workspace_id": "workspace-1", "name": "Workspace 1"},
            {"workspace_id": "workspace-2", "name": "Workspace 2"},
        ]
        self.mock_client.get.return_value = mock_response
        result = self.workspace_api.list()
        self.mock_client.get.assert_called_once_with("workspace/all/")
        self.assertEqual(result, mock_response)

    def test_get(self):
        mock_response = {"workspace_id": "workspace-1", "name": "Workspace 1"}
        self.mock_client.get.return_value = mock_response
        result = self.workspace_api.get("workspace-1")
        self.mock_client.get.assert_called_once_with("workspace/workspace-1")
        self.assertEqual(result, mock_response)

    def test_update_name_and_description(self):
        self.workspace_api.update("workspace-1", name="Updated Name", description="Updated Description")
        self.mock_client.patch.assert_called_once_with(
            "workspace/update/workspace-1",
            data={"name": "Updated Name", "description": "Updated Description"},
        )

    def test_update_name_only(self):
        self.workspace_api.update("workspace-1", name="Updated Name")
        self.mock_client.patch.assert_called_once_with(
            "workspace/update/workspace-1",
            data={"name": "Updated Name"},
        )

    def test_update_developer_access(self):
        self.workspace_api.update("workspace-1", developer_access=True)
        self.mock_client.patch.assert_called_once_with(
            "workspace/update/workspace-1",
            data={"developer_access": True},
        )

    def test_update_no_changes(self):
        self.workspace_api.update("workspace-1")
        self.mock_client.patch.assert_called_once_with(
            "workspace/update/workspace-1",
            data={},
        )

    def test_invalid_workspace_id(self):
        self.mock_client.get.side_effect = Exception("Workspace not found")
        with self.assertRaises(Exception) as context:
            self.workspace_api.get("invalid-id")
        self.assertEqual(str(context.exception), "Workspace not found")

    def test_empty_workspace_list(self):
        self.mock_client.get.return_value = []
        result = self.workspace_api.list()
        self.assertEqual(result, [])


if __name__ == '__main__':
    unittest.main()
