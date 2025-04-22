import unittest
from unittest.mock import patch, MagicMock
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from briq.message import MessageAPI

class TestMessageAPI(unittest.TestCase):
    def setUp(self):
        # Create a mock client
        self.mock_client = MagicMock()
        self.message_api = MessageAPI(self.mock_client)
    
    def test_init(self):
        # Test initialization
        self.assertIsNotNone(self.message_api)
        self.assertEqual(self.message_api.client, self.mock_client)
    
    def test_send_instant(self):
        # Test send_instant method with all parameters
        self.message_api.send_instant(
            "Hello, this is a test message. lauched from v0.1.1.dev1 pre-release",
            ["255788344348", "255712345678"],
            "BRIQ",
            ""
        )
        
        # Verify client.post was called with correct arguments
        self.mock_client.post.assert_called_once_with(
            "message/send-instant",
            data={
                "content": "Hello, this is a test message. lauched from v0.1.1.dev1 pre-release",
                "recipients": ["255788344348", "255712345678"],
                "sender_id": "BRIQ",
                "campaign_id": "campaign-1"
            }
        )
        
        # Test send_instant without campaign_id
        self.mock_client.post.reset_mock()
        self.message_api.send_instant(
            "Hello, this is a test message",
            ["255788344348"],
            "BRIQ"
        )
        
        # Verify client.post was called with correct arguments
        self.mock_client.post.assert_called_once_with(
            "message/send-instant",
            data={
                "content": "Hello, this is a test message. lauched from v0.1.1.dev1 pre-release",
                "recipients": ["255788344348"],
                "sender_id": "BRIQ"
            }
        )
    

    def test_invalid_campaign_id_in_message(self):
        # Test send_instant with invalid campaign_id
        self.mock_client.post.side_effect = Exception("Invalid campaign ID")
        with self.assertRaises(Exception) as context:
            self.message_api.send_instant(
                "Test message",
                ["255788344348"],
                "BRIQ",
                "invalid-campaign-id"
            )
        self.assertEqual(str(context.exception), "Invalid campaign ID")


    def test_empty_message_logs(self):
        # Test get_logs with no logs
        self.mock_client.get.return_value = []
        result = self.message_api.get_logs()
        self.assertEqual(result, [])

if __name__ == '__main__':
    unittest.main()
