import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from briq.client import Client
from briq.exceptions import BriqAPIError
from briq.whatsapp import (
    DOCUMENT_MAX_BYTES,
    IMAGE_MAX_BYTES,
    VIDEO_MAX_BYTES,
    WINDOW_CLOSED,
    WhatsAppAPI,
    assert_media_size,
)


def _json_response(payload, status=200):
    mock_response = MagicMock()
    mock_response.status_code = status
    mock_response.reason = "OK" if status < 400 else "Error"
    mock_response.content = b"{}" if payload is not None else b""
    mock_response.json.return_value = payload
    return mock_response


class TestWhatsAppAPI(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        self.wa = WhatsAppAPI(self.mock_client)

    def test_list_conversations(self):
        self.wa.list_conversations(status="unread", sender="255712345678", limit=20)
        self.mock_client.get.assert_called_once_with(
            "whatsapp/conversations",
            params={"status": "unread", "sender": "255712345678", "limit": 20},
        )

    def test_get_conversation(self):
        self.wa.get_conversation("conv-1")
        self.mock_client.get.assert_called_once_with("whatsapp/conversations/conv-1")

    def test_inbox_summary(self):
        self.wa.inbox_summary(sender="1107264639145282")
        self.mock_client.get.assert_called_once_with(
            "whatsapp/conversations/summary",
            params={"sender": "1107264639145282"},
        )

    def test_mark_read(self):
        self.wa.mark_read("conv-1", up_to="2026-06-24T09:12:00Z")
        self.mock_client.post.assert_called_once_with(
            "whatsapp/conversations/conv-1/read",
            data={"up_to": "2026-06-24T09:12:00Z"},
        )

    def test_delete_conversation(self):
        self.wa.delete_conversation("conv-1")
        self.mock_client.delete.assert_called_once_with("whatsapp/conversations/conv-1")

    def test_send_text(self):
        self.wa.send_text("Thanks, your order ships today.", to="255712345678")
        self.mock_client.post.assert_called_once_with(
            "whatsapp/messages/text",
            data={"body": "Thanks, your order ships today.", "to": "255712345678"},
        )

    def test_send_template(self):
        self.wa.send_template("order_update", to="255712345678", variables={"1": "A1234"})
        self.mock_client.post.assert_called_once_with(
            "whatsapp/messages/template",
            data={
                "template_name": "order_update",
                "to": "255712345678",
                "variables": {"1": "A1234"},
            },
        )

    def test_send_image(self):
        self.wa.send_image(
            to="255712345678",
            media_url="https://example.com/receipt.jpg",
            caption="Your receipt",
            size_bytes=1024,
        )
        self.mock_client.post.assert_called_once_with(
            "whatsapp/messages/image",
            data={
                "to": "255712345678",
                "media_url": "https://example.com/receipt.jpg",
                "caption": "Your receipt",
            },
        )

    def test_send_image_rejects_oversize(self):
        with self.assertRaises(BriqAPIError) as ctx:
            self.wa.send_image(
                to="255712345678",
                media_url="https://example.com/huge.jpg",
                size_bytes=IMAGE_MAX_BYTES + 1,
            )
        self.assertEqual(ctx.exception.code, "MEDIA_TOO_LARGE")
        self.mock_client.post.assert_not_called()

    def test_send_video(self):
        self.wa.send_video(to="255712345678", media_url="https://example.com/demo.mp4")
        self.mock_client.post.assert_called_once_with(
            "whatsapp/messages/video",
            data={"to": "255712345678", "media_url": "https://example.com/demo.mp4"},
        )

    def test_send_video_rejects_oversize(self):
        with self.assertRaises(BriqAPIError):
            self.wa.send_video(
                to="255712345678",
                media_url="https://example.com/demo.mp4",
                size_bytes=VIDEO_MAX_BYTES + 1,
            )
        self.mock_client.post.assert_not_called()

    def test_send_document(self):
        self.wa.send_document(
            to="255712345678",
            media_url="https://example.com/invoice.pdf",
            filename="Invoice-A1234.pdf",
            size_bytes=DOCUMENT_MAX_BYTES,
        )
        kwargs = self.mock_client.post.call_args
        self.assertEqual(kwargs.args[0], "whatsapp/messages/document")
        self.assertEqual(kwargs.kwargs["data"]["filename"], "Invoice-A1234.pdf")

    def test_send_audio(self):
        self.wa.send_audio(to="255712345678", file_id="file-1")
        self.mock_client.post.assert_called_once_with(
            "whatsapp/messages/audio",
            data={"to": "255712345678", "file_id": "file-1"},
        )

    def test_send_interactive(self):
        interactive = {"type": "button", "body": {"text": "OK?"}}
        self.wa.send_interactive(interactive, conversation_id="conv-1")
        self.mock_client.post.assert_called_once_with(
            "whatsapp/messages/interactive",
            data={"interactive": interactive, "conversation_id": "conv-1"},
        )

    def test_list_messages(self):
        self.wa.list_messages(conversation_id="conv-1", direction="inbound", limit=100)
        self.mock_client.get.assert_called_once_with(
            "whatsapp/messages",
            params={"conversation_id": "conv-1", "direction": "inbound", "limit": 100},
        )

    def test_get_status(self):
        self.wa.get_status("msg-1")
        self.mock_client.get.assert_called_once_with("whatsapp/messages/msg-1")

    def test_send_read_receipt(self):
        self.wa.send_read_receipt("msg-1")
        self.mock_client.post.assert_called_once_with("whatsapp/messages/msg-1/read")

    def test_list_senders(self):
        self.wa.list_senders(is_active=True)
        self.mock_client.get.assert_called_once_with(
            "whatsapp/senders",
            params={"is_active": "true"},
        )

    def test_get_sender(self):
        self.wa.get_sender("sender-1")
        self.mock_client.get.assert_called_once_with("whatsapp/senders/sender-1")

    def test_list_templates_repeatable_filters(self):
        self.wa.list_templates(status=["APPROVED", "PAUSED"], category="UTILITY", language="en")
        self.mock_client.get.assert_called_once_with(
            "whatsapp/templates",
            params={"status": ["APPROVED", "PAUSED"], "category": "UTILITY", "language": "en"},
        )

    def test_get_template(self):
        self.wa.get_template("tpl-1")
        self.mock_client.get.assert_called_once_with("whatsapp/templates/tpl-1")

    def test_assert_media_size_allows_limit(self):
        assert_media_size("image", IMAGE_MAX_BYTES)


class TestWhatsAppHTTP(unittest.TestCase):
    def setUp(self):
        self.client = Client(api_key="test-api-key-value")

    def test_client_exposes_whatsapp(self):
        self.assertIsInstance(self.client.whatsapp, WhatsAppAPI)

    @patch("requests.Session.request")
    def test_user_agent_is_briq_python(self, mock_request):
        mock_request.return_value = _json_response({"success": True, "data": {"items": []}})
        self.client.whatsapp.list_conversations()
        headers = mock_request.call_args.kwargs["headers"]
        self.assertTrue(headers["User-Agent"].startswith("Briq-Python/"))

    @patch("requests.Session.request")
    def test_window_closed_is_briq_api_error(self, mock_request):
        mock_request.return_value = _json_response(
            {
                "success": False,
                "data": None,
                "errors": [
                    {
                        "code": WINDOW_CLOSED,
                        "message": "The 24-hour window is closed. Send a template.",
                        "field": None,
                    }
                ],
                "request_id": "req-wa-1",
            },
            status=422,
        )
        with self.assertRaises(BriqAPIError) as ctx:
            self.client.whatsapp.send_text("hello", to="255712345678")
        self.assertEqual(ctx.exception.code, WINDOW_CLOSED)
        self.assertEqual(ctx.exception.status_code, 422)
        self.assertEqual(ctx.exception.request_id, "req-wa-1")

    @patch("requests.Session.request")
    def test_send_text_path(self, mock_request):
        mock_request.return_value = _json_response(
            {"success": True, "data": {"message_id": "msg-1", "status": "pending"}},
            status=202,
        )
        self.client.whatsapp.send_text("Thanks", to="255712345678")
        kwargs = mock_request.call_args.kwargs
        self.assertEqual(kwargs["url"], "http://karibu.briq.tz/v1/whatsapp/messages/text")
        self.assertEqual(kwargs["json"]["body"], "Thanks")
        self.assertEqual(kwargs["headers"]["X-API-Key"], "test-api-key-value")


if __name__ == "__main__":
    unittest.main()
