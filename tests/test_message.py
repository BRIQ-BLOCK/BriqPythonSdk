import os
import sys
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from briq.message import MessageAPI


class TestMessageAPI(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        self.message_api = MessageAPI(self.mock_client)

    def test_init(self):
        self.assertIsNotNone(self.message_api)
        self.assertEqual(self.message_api.client, self.mock_client)

    def test_send_instant_basic(self):
        self.message_api.send_instant("Hello", ["255788344348"], "BRIQ")
        self.mock_client.post.assert_called_once_with(
            "message/send-instant",
            data={"content": "Hello", "recipients": ["255788344348"], "sender_id": "BRIQ", "flash": False},
            extra_headers=None,
        )

    def test_send_instant_with_campaign_id(self):
        self.message_api.send_instant("Hello", ["255788344348"], "BRIQ", campaign_id="camp-1")
        call_data = self.mock_client.post.call_args.kwargs["data"]
        self.assertEqual(call_data["campaign_id"], "camp-1")

    def test_send_instant_with_groups(self):
        self.message_api.send_instant("Hello", ["255788344348"], "BRIQ", groups=["g1", "g2"])
        call_data = self.mock_client.post.call_args.kwargs["data"]
        self.assertEqual(call_data["groups"], ["g1", "g2"])

    def test_send_instant_flash(self):
        self.message_api.send_instant("Hello", ["255788344348"], "BRIQ", flash=True)
        call_data = self.mock_client.post.call_args.kwargs["data"]
        self.assertTrue(call_data["flash"])

    def test_send_instant_scheduled(self):
        self.message_api.send_instant("Hello", ["255788344348"], "BRIQ", send_at="2025-12-11T15:30:00Z")
        call_data = self.mock_client.post.call_args.kwargs["data"]
        self.assertEqual(call_data["send_at"], "2025-12-11T15:30:00Z")

    def test_send_instant_with_app_id(self):
        self.message_api.send_instant("Hello", ["255788344348"], "BRIQ", app_id="my-app-id")
        call_kwargs = self.mock_client.post.call_args.kwargs
        self.assertEqual(call_kwargs["extra_headers"], {"X-App-ID": "my-app-id"})

    def test_send_campaign_basic(self):
        self.message_api.send_campaign("camp-1", "Hello everyone", "BRIQ")
        self.mock_client.post.assert_called_once_with(
            "message/send-campaign",
            data={"campaign_id": "camp-1", "content": "Hello everyone", "sender_id": "BRIQ"},
            extra_headers=None,
        )

    def test_send_campaign_with_schedule(self):
        self.message_api.send_campaign(
            "camp-1", "Hello", "BRIQ",
            start_date="2025-01-01T08:00:00Z",
            end_date="2025-01-31T08:00:00Z",
            frequency="daily",
        )
        call_data = self.mock_client.post.call_args.kwargs["data"]
        self.assertEqual(call_data["start_date"], "2025-01-01T08:00:00Z")
        self.assertEqual(call_data["frequency"], "daily")

    def test_send_campaign_with_app_id(self):
        self.message_api.send_campaign("camp-1", "Hello", "BRIQ", app_id="my-app-id")
        call_kwargs = self.mock_client.post.call_args.kwargs
        self.assertEqual(call_kwargs["extra_headers"], {"X-App-ID": "my-app-id"})

    def test_get_logs(self):
        self.mock_client.get.return_value = []
        result = self.message_api.get_logs()
        self.mock_client.get.assert_called_once_with("message/logs")
        self.assertEqual(result, [])

    def test_get_history(self):
        self.mock_client.get.return_value = []
        self.message_api.get_history()
        self.mock_client.get.assert_called_once_with("message/history")

    def test_get_history_by_recipient(self):
        self.mock_client.get.return_value = []
        self.message_api.get_history_by_recipient("255788344348")
        self.mock_client.get.assert_called_once_with("message/history/recipient/255788344348")

    def test_get_message_log(self):
        self.mock_client.get.return_value = {"message_id": "msg-1"}
        result = self.message_api.get_message_log("msg-1")
        self.mock_client.get.assert_called_once_with("message/message-log/msg-1")
        self.assertEqual(result, {"message_id": "msg-1"})

    def test_send_instant_error_propagates(self):
        self.mock_client.post.side_effect = Exception("Invalid campaign ID")
        with self.assertRaises(Exception) as context:
            self.message_api.send_instant("Test", ["255788344348"], "BRIQ", campaign_id="bad-id")
        self.assertEqual(str(context.exception), "Invalid campaign ID")


if __name__ == '__main__':
    unittest.main()
