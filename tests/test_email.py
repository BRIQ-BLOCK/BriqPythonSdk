import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from briq.client import Client
from briq.email import EmailAPI
from briq.exceptions import BriqAPIError, BriqAuthError, BriqValidationError


def _json_response(payload, status=200):
    mock_response = MagicMock()
    mock_response.status_code = status
    mock_response.reason = "OK" if status < 400 else "Error"
    mock_response.content = b"{}" if payload is not None else b""
    mock_response.json.return_value = payload
    return mock_response


class TestEmailAPI(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        self.email = EmailAPI(self.mock_client)

    def test_list_senders(self):
        self.email.list_senders()
        self.mock_client.get.assert_called_once_with("email/senders")

    def test_get_sender(self):
        self.email.get_sender("sender-1")
        self.mock_client.get.assert_called_once_with("email/senders/sender-1")

    def test_validate_omits_none(self):
        self.email.validate(to=["asha@example.com"], subject="Receipt")
        self.mock_client.post.assert_called_once_with(
            "email/validate",
            data={"to": ["asha@example.com"], "subject": "Receipt"},
        )

    def test_send_messages_auto_idempotency_key(self):
        self.mock_client.post.return_value = {"success": True, "data": {"job_id": "job-1"}}
        with patch("briq.email.uuid.uuid4", return_value="auto-key-123"):
            self.email.send_messages(
                [{"to": "asha@example.com", "subject": "Hi", "text": "Hello"}],
                transactional=True,
            )
        kwargs = self.mock_client.post.call_args.kwargs
        self.assertEqual(kwargs["data"]["messages"][0]["to"], "asha@example.com")
        self.assertTrue(kwargs["data"]["transactional"])
        self.assertEqual(kwargs["extra_headers"]["Idempotency-Key"], "auto-key-123")

    def test_send_messages_passed_idempotency_key(self):
        self.email.send_messages(
            [{"to": "asha@example.com", "subject": "Hi", "text": "Hello"}],
            idempotency_key="order-10421",
        )
        kwargs = self.mock_client.post.call_args.kwargs
        self.assertEqual(kwargs["extra_headers"]["Idempotency-Key"], "order-10421")

    def test_send_messages_retries_503_send_failed_same_key(self):
        failed = BriqAPIError("queued failed", status_code=503, code="SEND_FAILED")
        ok = {"success": True, "data": {"job_id": "job-9"}}
        self.mock_client.post.side_effect = [failed, ok]
        with patch("briq.email.time.sleep"):
            result = self.email.send_messages(
                [{"to": "asha@example.com", "subject": "Hi", "text": "Hello"}],
                idempotency_key="stable-key",
            )
        self.assertEqual(result["data"]["job_id"], "job-9")
        self.assertEqual(self.mock_client.post.call_count, 2)
        keys = [
            call.kwargs["extra_headers"]["Idempotency-Key"]
            for call in self.mock_client.post.call_args_list
        ]
        self.assertEqual(keys, ["stable-key", "stable-key"])

    def test_send_messages_retries_503_send_allowed(self):
        failed = BriqAPIError("try again", status_code=503, code="SEND_ALLOWED")
        self.mock_client.post.side_effect = [failed, {"success": True}]
        with patch("briq.email.time.sleep"):
            self.email.send_messages(
                [{"to": "asha@example.com", "subject": "Hi", "text": "Hello"}],
                idempotency_key="k",
            )
        self.assertEqual(self.mock_client.post.call_count, 2)

    def test_send_messages_does_not_retry_422(self):
        err = BriqAPIError("no subject", status_code=422, code="SUBJECT_REQUIRED")
        self.mock_client.post.side_effect = err
        with self.assertRaises(BriqAPIError) as ctx:
            self.email.send_messages([{"to": "asha@example.com", "text": "Hello"}])
        self.assertEqual(ctx.exception.code, "SUBJECT_REQUIRED")
        self.assertEqual(self.mock_client.post.call_count, 1)

    def test_send_messages_does_not_retry_other_503(self):
        err = BriqAPIError("unavailable", status_code=503, code="RATE_LIMIT_EXCEEDED")
        self.mock_client.post.side_effect = err
        with self.assertRaises(BriqAPIError):
            self.email.send_messages([{"to": "asha@example.com", "subject": "Hi", "text": "Hello"}])
        self.assertEqual(self.mock_client.post.call_count, 1)

    def test_send_broadcast(self):
        self.email.send_broadcast(
            "We open Saturday",
            to=["ops@duka.co.tz"],
            group_ids=["group-1"],
            text="Come by before noon.",
        )
        self.mock_client.post.assert_called_once_with(
            "email/broadcasts",
            data={
                "subject": "We open Saturday",
                "to": ["ops@duka.co.tz"],
                "group_ids": ["group-1"],
                "text": "Come by before noon.",
            },
        )

    def test_list_messages_filters(self):
        self.email.list_messages(status="bounced", job_id="job-1", page=2, limit=20)
        self.mock_client.get.assert_called_once_with(
            "email/messages",
            params={"status": "bounced", "job_id": "job-1", "page": 2, "limit": 20},
        )

    def test_get_message(self):
        self.email.get_message("msg-1")
        self.mock_client.get.assert_called_once_with("email/messages/msg-1")

    def test_retry_messages(self):
        self.email.retry_messages(["msg-1", "msg-2"])
        self.mock_client.post.assert_called_once_with(
            "email/messages/retry",
            data={"message_ids": ["msg-1", "msg-2"]},
        )

    def test_get_job(self):
        self.email.get_job("job-1")
        self.mock_client.get.assert_called_once_with("email/jobs/job-1")

    def test_list_scheduled_jobs(self):
        self.email.list_scheduled_jobs()
        self.mock_client.get.assert_called_once_with("email/jobs")

    def test_cancel_job(self):
        self.email.cancel_job("job-1")
        self.mock_client.delete.assert_called_once_with("email/jobs/job-1")

    def test_wait_job_until_counts_settle(self):
        pending = {"success": True, "data": {"counts": {"queued": 2}}}
        done = {"success": True, "data": {"counts": {"sent": 2}}}
        self.mock_client.get.side_effect = [pending, done]
        with patch("briq.email.time.sleep"):
            result = self.email.wait_job("job-1", timeout=5, interval=0)
        self.assertEqual(result["data"]["counts"]["sent"], 2)
        self.assertEqual(self.mock_client.get.call_count, 2)

    def test_wait_job_timeout(self):
        self.mock_client.get.return_value = {"success": True, "data": {"counts": {"queued": 1}}}
        with (
            patch("briq.email.time.sleep"),
            patch("briq.email.time.monotonic", side_effect=[0.0, 0.0, 10.0]),
            self.assertRaises(TimeoutError),
        ):
            self.email.wait_job("job-1", timeout=5, interval=0)


class TestEmailHTTP(unittest.TestCase):
    def setUp(self):
        self.client = Client(api_key="test-api-key-value")

    def test_client_exposes_email(self):
        self.assertIsInstance(self.client.email, EmailAPI)

    @patch("requests.Session.request")
    def test_user_agent_is_briq_python(self, mock_request):
        mock_request.return_value = _json_response({"success": True, "data": {"items": []}})
        self.client.email.list_senders()
        headers = mock_request.call_args.kwargs["headers"]
        self.assertTrue(headers["User-Agent"].startswith("Briq-Python/"))
        self.assertNotIn("python-requests", headers["User-Agent"])

    @patch("requests.Session.request")
    def test_envelope_error_is_briq_api_error(self, mock_request):
        mock_request.return_value = _json_response(
            {
                "success": False,
                "data": None,
                "errors": [
                    {
                        "code": "INSUFFICIENT_ALLOCATION",
                        "message": "Not enough emails left.",
                        "field": None,
                        "meta": {"emails_required": 10, "emails_available": 2},
                    }
                ],
                "request_id": "req-1",
            },
            status=402,
        )
        with self.assertRaises(BriqAPIError) as ctx:
            self.client.email.send_messages(
                [{"to": "asha@example.com", "subject": "Hi", "text": "Hello"}]
            )
        self.assertEqual(ctx.exception.code, "INSUFFICIENT_ALLOCATION")
        self.assertEqual(ctx.exception.status_code, 402)
        self.assertEqual(ctx.exception.request_id, "req-1")
        self.assertEqual(ctx.exception.errors[0]["meta"]["emails_required"], 10)

    @patch("requests.Session.request")
    def test_fastapi_422_still_validation_error(self, mock_request):
        mock_request.return_value = _json_response(
            {"detail": [{"loc": ["body", "name"], "msg": "field required", "type": "missing"}]},
            status=422,
        )
        with self.assertRaises(BriqValidationError) as ctx:
            self.client.request("POST", "workspace/create/", data={})
        self.assertEqual(len(ctx.exception.detail), 1)

    @patch("requests.Session.request")
    def test_401_still_auth_error(self, mock_request):
        mock_request.return_value = _json_response(
            {
                "success": False,
                "data": None,
                "errors": [{"code": "UNAUTHORIZED", "message": "Missing key"}],
                "request_id": "req-2",
            },
            status=401,
        )
        with self.assertRaises(BriqAuthError):
            self.client.email.list_senders()

    @patch("requests.Session.request")
    def test_send_path_and_idempotency_header(self, mock_request):
        mock_request.return_value = _json_response(
            {"success": True, "data": {"job_id": "job-1", "status": "queued"}},
            status=202,
        )
        self.client.email.send_messages(
            [{"to": "asha@example.com", "subject": "Hi", "text": "Hello"}],
            idempotency_key="fixed-key",
        )
        kwargs = mock_request.call_args.kwargs
        self.assertEqual(kwargs["url"], "http://karibu.briq.tz/v1/email/messages")
        self.assertEqual(kwargs["headers"]["Idempotency-Key"], "fixed-key")
        self.assertEqual(kwargs["headers"]["X-API-Key"], "test-api-key-value")


if __name__ == "__main__":
    unittest.main()
