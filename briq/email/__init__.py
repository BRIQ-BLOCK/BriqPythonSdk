"""
Karibu Email module for the Briq API.

Documented surfaces only — ``/v1/email/senders``, ``/messages``,
``/broadcasts``, ``/validate``, ``/jobs``. There is no attachment-send API.
"""

from __future__ import annotations

import time
import uuid
from typing import TYPE_CHECKING

from ..exceptions import BriqAPIError

if TYPE_CHECKING:
    from ..client import Client

# Documented retryable send failure is 503 SEND_FAILED. SEND_ALLOWED is
# accepted if the platform emits it on the same 503 retry path.
_RETRYABLE_SEND_CODES = frozenset({"SEND_FAILED", "SEND_ALLOWED"})
_DEFAULT_SEND_RETRIES = 2


def _omit_none(payload: dict) -> dict:
    return {key: value for key, value in payload.items() if value is not None}


class EmailAPI:
    """
    Karibu Email API for Briq.

    Workspace-scoped via ``X-API-Key``. Helpers map 1:1 to
    https://docs.briq.tz/Karibu-Email/index.md
    """

    def __init__(self, client: Client) -> None:
        self.client = client

    def list_senders(self) -> dict:
        """GET /v1/email/senders — list sender profiles for this workspace."""
        return self.client.get("email/senders")

    def get_sender(self, sender_id: str) -> dict:
        """GET /v1/email/senders/{sender_id} — one sender profile by id."""
        return self.client.get(f"email/senders/{sender_id}")

    def validate(
        self,
        *,
        sender_id: str | None = None,
        to: list[str] | None = None,
        group_ids: list[str] | None = None,
        subject: str | None = None,
        text: str | None = None,
        html: str | None = None,
        send_at: str | None = None,
    ) -> dict:
        """
        POST /v1/email/validate — preflight a send.

        Runs the same checks a real send runs. Nothing is queued or charged.
        Preflight issue codes in ``data.errors`` / ``data.warnings`` are
        lower-case and distinct from refused-send codes.
        """
        return self.client.post(
            "email/validate",
            data=_omit_none(
                {
                    "sender_id": sender_id,
                    "to": to,
                    "group_ids": group_ids,
                    "subject": subject,
                    "text": text,
                    "html": html,
                    "send_at": send_at,
                }
            ),
        )

    def send_messages(
        self,
        messages: list[dict],
        *,
        sender_id: str | None = None,
        template_id: str | None = None,
        send_at: str | None = None,
        transactional: bool | None = None,
        idempotency_key: str | None = None,
        max_retries: int = _DEFAULT_SEND_RETRIES,
    ) -> dict:
        """
        POST /v1/email/messages — send 1–500 individually addressed emails.

        An ``Idempotency-Key`` is always sent: the caller-supplied value, or a
        generated UUID. The same key is reused across documented 503
        ``SEND_FAILED`` / ``SEND_ALLOWED`` retries. Other failures are not retried.

        There is no attachment field on this endpoint.
        """
        data = _omit_none(
            {
                "messages": messages,
                "sender_id": sender_id,
                "template_id": template_id,
                "send_at": send_at,
                "transactional": transactional,
            }
        )
        key = idempotency_key or str(uuid.uuid4())
        headers = {"Idempotency-Key": key}
        last_error: BriqAPIError | None = None
        attempts = max(1, max_retries + 1)
        for attempt in range(attempts):
            try:
                return self.client.post(
                    "email/messages",
                    data=data,
                    extra_headers=headers,
                )
            except BriqAPIError as exc:
                if (
                    attempt < attempts - 1
                    and exc.status_code == 503
                    and exc.code in _RETRYABLE_SEND_CODES
                ):
                    last_error = exc
                    time.sleep(min(8.0, 1.0 * (2**attempt)))
                    continue
                raise
        assert last_error is not None
        raise last_error

    def send_broadcast(
        self,
        subject: str,
        *,
        sender_id: str | None = None,
        to: list[str] | None = None,
        group_ids: list[str] | None = None,
        text: str | None = None,
        html: str | None = None,
        reply_to: str | None = None,
        send_at: str | None = None,
    ) -> dict:
        """
        POST /v1/email/broadcasts — one subject and body to many recipients.

        Address recipients with ``to``, ``group_ids``, or both. There is no
        ``transactional`` flag on broadcasts.
        """
        return self.client.post(
            "email/broadcasts",
            data=_omit_none(
                {
                    "subject": subject,
                    "sender_id": sender_id,
                    "to": to,
                    "group_ids": group_ids,
                    "text": text,
                    "html": html,
                    "reply_to": reply_to,
                    "send_at": send_at,
                }
            ),
        )

    def list_messages(
        self,
        *,
        status: str | None = None,
        to: str | None = None,
        job_id: str | None = None,
        sender_id: str | None = None,
        page: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """GET /v1/email/messages — page workspace email history, newest first."""
        return self.client.get(
            "email/messages",
            params=_omit_none(
                {
                    "status": status,
                    "to": to,
                    "job_id": job_id,
                    "sender_id": sender_id,
                    "page": page,
                    "limit": limit,
                }
            )
            or None,
        )

    def get_message(self, message_id: str) -> dict:
        """GET /v1/email/messages/{message_id} — one email plus event history."""
        return self.client.get(f"email/messages/{message_id}")

    def retry_messages(self, message_ids: list[str]) -> dict:
        """
        POST /v1/email/messages/retry — re-arm ``failed`` / ``bounced`` messages.

        Never re-charged. Ineligible ids are reported in ``data.rejected``.
        """
        return self.client.post("email/messages/retry", data={"message_ids": message_ids})

    def get_job(self, job_id: str) -> dict:
        """GET /v1/email/jobs/{job_id} — status rollup for one send. Poll after 202."""
        return self.client.get(f"email/jobs/{job_id}")

    def list_scheduled_jobs(self) -> dict:
        """GET /v1/email/jobs — sends still waiting for their ``send_at``."""
        return self.client.get("email/jobs")

    def cancel_job(self, job_id: str) -> dict:
        """DELETE /v1/email/jobs/{job_id} — cancel a scheduled send and release emails."""
        return self.client.delete(f"email/jobs/{job_id}")

    def wait_job(
        self,
        job_id: str,
        *,
        timeout: float = 60.0,
        interval: float = 1.0,
    ) -> dict:
        """
        Poll ``GET /v1/email/jobs/{job_id}`` until the send is finished.

        A send is done when ``queued`` and ``scheduled`` are both absent from
        ``data.counts``. Raises ``TimeoutError`` if ``timeout`` elapses first.
        """
        deadline = time.monotonic() + timeout
        while True:
            result = self.get_job(job_id)
            data = result.get("data") if isinstance(result, dict) else None
            counts = data.get("counts") if isinstance(data, dict) else None
            if isinstance(counts, dict) and "queued" not in counts and "scheduled" not in counts:
                return result
            if time.monotonic() >= deadline:
                raise TimeoutError(f"Timed out waiting for email job {job_id}")
            time.sleep(interval)
