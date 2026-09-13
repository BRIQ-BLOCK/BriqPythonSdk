import os
import sys
import unittest
from unittest.mock import MagicMock, patch

import requests as req

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from briq.client import Client
from briq.exceptions import BriqAPIError, BriqAuthError, BriqRequestError, BriqValidationError


class TestClient(unittest.TestCase):
    def setUp(self):
        self.client = Client(api_key="test-api-key-value")

    def test_init(self):
        self.assertIsNotNone(self.client)
        self.assertEqual(self.client.config.api_key, "test-api-key-value")
        self.assertEqual(self.client.config.base_url, "http://karibu.briq.tz")

        client = Client(api_key="test-api-key-value", base_url="http://meetpay.africa")
        self.assertEqual(client.config.base_url, "http://meetpay.africa")

    def test_set_api_key(self):
        self.client.set_api_key("new_api_key")
        self.assertEqual(self.client.config.api_key, "new_api_key")

    # --- URL routing tests (Phase 0) ---

    @patch("requests.Session.request")
    def test_request_v1_prefix(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'{"key": "value"}'
        mock_response.json.return_value = {"key": "value"}
        mock_request.return_value = mock_response

        result = self.client.request("GET", "test/endpoint")

        call_kwargs = mock_request.call_args.kwargs
        self.assertEqual(call_kwargs["method"], "GET")
        self.assertEqual(call_kwargs["url"], "http://karibu.briq.tz/v1/test/endpoint")
        self.assertEqual(call_kwargs["headers"]["X-API-Key"], "test-api-key-value")
        self.assertTrue(call_kwargs["headers"]["User-Agent"].startswith("Briq-Python/"))
        self.assertEqual(call_kwargs["json"], None)
        self.assertEqual(call_kwargs["params"], None)
        self.assertEqual(result, {"key": "value"})

    @patch("requests.Session.request")
    def test_request_root_prefix(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"{}"
        mock_response.json.return_value = {}
        mock_request.return_value = mock_response

        self.client.request("GET", "version", prefix="", auth="none")

        call_kwargs = mock_request.call_args
        self.assertEqual(call_kwargs.kwargs["url"], "http://karibu.briq.tz/version")

    @patch("requests.Session.request")
    def test_request_developer_apps_prefix(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"[]"
        mock_response.json.return_value = []
        mock_request.return_value = mock_response

        self.client.config.access_token = "fake-bearer-token"
        self.client.request("GET", "developer-apps/", prefix="", auth="bearer")

        call_kwargs = mock_request.call_args
        self.assertEqual(call_kwargs.kwargs["url"], "http://karibu.briq.tz/developer-apps/")

    @patch("requests.Session.request")
    def test_request_workspace_v1(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"[]"
        mock_response.json.return_value = []
        mock_request.return_value = mock_response

        self.client.request("GET", "workspace/all/")

        call_kwargs = mock_request.call_args
        self.assertEqual(call_kwargs.kwargs["url"], "http://karibu.briq.tz/v1/workspace/all/")

    # --- Auth tests ---

    @patch("requests.Session.request")
    def test_bearer_auth_header(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"{}"
        mock_response.json.return_value = {}
        mock_request.return_value = mock_response

        self.client.config.access_token = "my-token-123"
        self.client.request("GET", "developer-apps/", prefix="", auth="bearer")

        headers = mock_request.call_args.kwargs["headers"]
        self.assertEqual(headers.get("Authorization"), "Bearer my-token-123")
        self.assertNotIn("X-API-Key", headers)

    def test_bearer_auth_without_token_raises(self):
        self.client.config.access_token = None
        with self.assertRaises(BriqAuthError):
            self.client.request("GET", "developer-apps/", prefix="", auth="bearer")

    # --- Error handling tests ---

    @patch("requests.Session.request")
    def test_request_auth_error(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = req.exceptions.HTTPError("401 Client Error")
        mock_request.return_value = mock_response

        with self.assertRaises(BriqAuthError):
            self.client.request("GET", "test/endpoint")

    @patch("requests.Session.request")
    def test_request_validation_error(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 422
        mock_response.content = (
            b'{"detail": [{"loc": ["body", "name"], "msg": "field required", "type": "missing"}]}'
        )
        mock_response.json.return_value = {
            "detail": [{"loc": ["body", "name"], "msg": "field required", "type": "missing"}]
        }
        mock_response.raise_for_status.side_effect = req.exceptions.HTTPError(
            "422 Unprocessable Entity"
        )
        mock_request.return_value = mock_response

        with self.assertRaises(BriqValidationError) as ctx:
            self.client.request("POST", "test/endpoint", data={})
        self.assertIsInstance(ctx.exception.detail, list)
        self.assertEqual(len(ctx.exception.detail), 1)

    @patch("requests.Session.request")
    def test_request_api_error(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.content = b'{"error": "Bad request"}'
        mock_response.json.return_value = {"error": "Bad request"}
        mock_response.raise_for_status.side_effect = req.exceptions.HTTPError("400 Client Error")
        mock_request.return_value = mock_response

        with self.assertRaises(BriqAPIError) as ctx:
            self.client.request("GET", "test/endpoint")
        self.assertEqual(ctx.exception.status_code, 400)

    @patch("requests.Session.request")
    def test_request_network_error(self, mock_request):
        import requests as req

        mock_request.side_effect = req.exceptions.RequestException("Connection error")

        with self.assertRaises(BriqRequestError):
            self.client.request("GET", "test/endpoint")

    # --- 204 / empty body ---

    @patch("requests.Session.request")
    def test_request_empty_response(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_response.content = b""
        mock_request.return_value = mock_response

        result = self.client.request("DELETE", "test/endpoint")
        self.assertEqual(result, {})

    # --- Convenience methods ---

    @patch("briq.client.Client.request")
    def test_get(self, mock_request):
        self.client.get("test/endpoint", params={"param": "value"})
        mock_request.assert_called_once_with(
            "GET",
            "test/endpoint",
            params={"param": "value"},
            prefix="v1",
            auth="api_key",
            extra_headers=None,
        )

    @patch("briq.client.Client.request")
    def test_post(self, mock_request):
        self.client.post("test/endpoint", data={"key": "value"})
        mock_request.assert_called_once_with(
            "POST",
            "test/endpoint",
            data={"key": "value"},
            prefix="v1",
            auth="api_key",
            extra_headers=None,
            files=None,
        )

    @patch("briq.client.Client.request")
    def test_patch(self, mock_request):
        self.client.patch("test/endpoint", data={"key": "value"})
        mock_request.assert_called_once_with(
            "PATCH",
            "test/endpoint",
            data={"key": "value"},
            prefix="v1",
            auth="api_key",
            extra_headers=None,
        )

    @patch("briq.client.Client.request")
    def test_delete(self, mock_request):
        self.client.delete("test/endpoint")
        mock_request.assert_called_once_with(
            "DELETE",
            "test/endpoint",
            prefix="v1",
            auth="api_key",
            extra_headers=None,
        )


if __name__ == "__main__":
    unittest.main()
