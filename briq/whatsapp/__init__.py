"""
Karibu WhatsApp module for the Briq API.

Documented surfaces only — conversations, messages, senders, and templates.
Inbound events stay on ``client.webhooks`` (``service_type="whatsapp"``).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..exceptions import BriqAPIError

if TYPE_CHECKING:
    from ..client import Client

IMAGE_MAX_BYTES = 5 * 1024 * 1024
VIDEO_MAX_BYTES = 16 * 1024 * 1024
AUDIO_MAX_BYTES = 16 * 1024 * 1024
DOCUMENT_MAX_BYTES = 100 * 1024 * 1024

WINDOW_CLOSED = "WINDOW_CLOSED"

_MEDIA_LIMITS = {
    "image": IMAGE_MAX_BYTES,
    "video": VIDEO_MAX_BYTES,
    "audio": AUDIO_MAX_BYTES,
    "document": DOCUMENT_MAX_BYTES,
}


def _omit_none(payload: dict) -> dict:
    return {key: value for key, value in payload.items() if value is not None}


def _bool_query(value: bool | None) -> str | None:
    if value is None:
        return None
    return "true" if value else "false"


def assert_media_size(kind: str, size_bytes: int) -> None:
    """Raise if ``size_bytes`` exceeds the documented WhatsApp limit for ``kind``."""
    limit = _MEDIA_LIMITS[kind]
    if size_bytes > limit:
        raise BriqAPIError(
            f"{kind} exceeds the documented WhatsApp size limit ({limit} bytes)",
            code="MEDIA_TOO_LARGE",
        )


class WhatsAppAPI:
    """
    Karibu WhatsApp API for Briq.

    Workspace-scoped via ``X-API-Key``. Message types other than templates
    require an open 24-hour window; a closed window is ``422 WINDOW_CLOSED``.
    """

    def __init__(self, client: Client) -> None:
        self.client = client

    # --- Conversations ---

    def list_conversations(
        self,
        *,
        sender: str | None = None,
        sender_id: str | None = None,
        recipient: str | None = None,
        status: str | None = None,
        search: str | None = None,
        since: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict:
        """GET /v1/whatsapp/conversations — threads, most recently active first."""
        return self.client.get(
            "whatsapp/conversations",
            params=_omit_none(
                {
                    "sender": sender,
                    "sender_id": sender_id,
                    "recipient": recipient,
                    "status": status,
                    "search": search,
                    "since": since,
                    "limit": limit,
                    "offset": offset,
                }
            )
            or None,
        )

    def get_conversation(self, conversation_id: str) -> dict:
        """GET /v1/whatsapp/conversations/{conversation_id}"""
        return self.client.get(f"whatsapp/conversations/{conversation_id}")

    def inbox_summary(
        self,
        *,
        sender: str | None = None,
        sender_id: str | None = None,
    ) -> dict:
        """GET /v1/whatsapp/conversations/summary — total / open / unread / unassigned."""
        return self.client.get(
            "whatsapp/conversations/summary",
            params=_omit_none({"sender": sender, "sender_id": sender_id}) or None,
        )

    def mark_read(self, conversation_id: str, *, up_to: str | None = None) -> dict:
        """
        POST /v1/whatsapp/conversations/{conversation_id}/read

        Clears inbox unread state. This is not a WhatsApp read receipt.
        """
        return self.client.post(
            f"whatsapp/conversations/{conversation_id}/read",
            data=_omit_none({"up_to": up_to}) or None,
        )

    def delete_conversation(self, conversation_id: str) -> dict:
        """DELETE /v1/whatsapp/conversations/{conversation_id} — soft-delete, one-way."""
        return self.client.delete(f"whatsapp/conversations/{conversation_id}")

    # --- Messages ---

    def send_text(
        self,
        body: str,
        *,
        to: str | None = None,
        sender: str | None = None,
        conversation_id: str | None = None,
        sender_id: str | None = None,
    ) -> dict:
        """
        POST /v1/whatsapp/messages/text

        Needs an open 24-hour window; otherwise ``422 WINDOW_CLOSED``.
        """
        return self.client.post(
            "whatsapp/messages/text",
            data=_omit_none(
                {
                    "body": body,
                    "to": to,
                    "sender": sender,
                    "conversation_id": conversation_id,
                    "sender_id": sender_id,
                }
            ),
        )

    def send_template(
        self,
        template_name: str,
        *,
        to: str | None = None,
        sender: str | None = None,
        conversation_id: str | None = None,
        sender_id: str | None = None,
        variables: dict[str, str] | None = None,
    ) -> dict:
        """
        POST /v1/whatsapp/messages/template

        Always allowed; reopens the 24-hour window. Only APPROVED templates send.
        """
        return self.client.post(
            "whatsapp/messages/template",
            data=_omit_none(
                {
                    "template_name": template_name,
                    "to": to,
                    "sender": sender,
                    "conversation_id": conversation_id,
                    "sender_id": sender_id,
                    "variables": variables,
                }
            ),
        )

    def send_image(
        self,
        *,
        to: str | None = None,
        sender: str | None = None,
        conversation_id: str | None = None,
        sender_id: str | None = None,
        media_url: str | None = None,
        file_id: str | None = None,
        caption: str | None = None,
        size_bytes: int | None = None,
    ) -> dict:
        """
        POST /v1/whatsapp/messages/image — JPEG/PNG, ≤5 MB. Needs an open window.
        """
        if size_bytes is not None:
            assert_media_size("image", size_bytes)
        return self.client.post(
            "whatsapp/messages/image",
            data=_omit_none(
                {
                    "to": to,
                    "sender": sender,
                    "conversation_id": conversation_id,
                    "sender_id": sender_id,
                    "media_url": media_url,
                    "file_id": file_id,
                    "caption": caption,
                }
            ),
        )

    def send_video(
        self,
        *,
        to: str | None = None,
        sender: str | None = None,
        conversation_id: str | None = None,
        sender_id: str | None = None,
        media_url: str | None = None,
        file_id: str | None = None,
        caption: str | None = None,
        size_bytes: int | None = None,
    ) -> dict:
        """
        POST /v1/whatsapp/messages/video — MP4/3GPP, ≤16 MB. Needs an open window.
        """
        if size_bytes is not None:
            assert_media_size("video", size_bytes)
        return self.client.post(
            "whatsapp/messages/video",
            data=_omit_none(
                {
                    "to": to,
                    "sender": sender,
                    "conversation_id": conversation_id,
                    "sender_id": sender_id,
                    "media_url": media_url,
                    "file_id": file_id,
                    "caption": caption,
                }
            ),
        )

    def send_document(
        self,
        *,
        to: str | None = None,
        sender: str | None = None,
        conversation_id: str | None = None,
        sender_id: str | None = None,
        media_url: str | None = None,
        file_id: str | None = None,
        caption: str | None = None,
        filename: str | None = None,
        size_bytes: int | None = None,
    ) -> dict:
        """
        POST /v1/whatsapp/messages/document — PDF/Office/text, ≤100 MB.
        Needs an open window.
        """
        if size_bytes is not None:
            assert_media_size("document", size_bytes)
        return self.client.post(
            "whatsapp/messages/document",
            data=_omit_none(
                {
                    "to": to,
                    "sender": sender,
                    "conversation_id": conversation_id,
                    "sender_id": sender_id,
                    "media_url": media_url,
                    "file_id": file_id,
                    "caption": caption,
                    "filename": filename,
                }
            ),
        )

    def send_audio(
        self,
        *,
        to: str | None = None,
        sender: str | None = None,
        conversation_id: str | None = None,
        sender_id: str | None = None,
        media_url: str | None = None,
        file_id: str | None = None,
        size_bytes: int | None = None,
    ) -> dict:
        """
        POST /v1/whatsapp/messages/audio — AAC/MP3/M4A/OGG-OPUS/AMR, ≤16 MB.
        No caption. Needs an open window.
        """
        if size_bytes is not None:
            assert_media_size("audio", size_bytes)
        return self.client.post(
            "whatsapp/messages/audio",
            data=_omit_none(
                {
                    "to": to,
                    "sender": sender,
                    "conversation_id": conversation_id,
                    "sender_id": sender_id,
                    "media_url": media_url,
                    "file_id": file_id,
                }
            ),
        )

    def send_interactive(
        self,
        interactive: dict,
        *,
        to: str | None = None,
        sender: str | None = None,
        conversation_id: str | None = None,
        sender_id: str | None = None,
    ) -> dict:
        """
        POST /v1/whatsapp/messages/interactive — buttons or list. Needs an open window.
        """
        return self.client.post(
            "whatsapp/messages/interactive",
            data=_omit_none(
                {
                    "interactive": interactive,
                    "to": to,
                    "sender": sender,
                    "conversation_id": conversation_id,
                    "sender_id": sender_id,
                }
            ),
        )

    def list_messages(
        self,
        *,
        conversation_id: str | None = None,
        message_type: str | None = None,
        status: str | None = None,
        direction: str | None = None,
        since: str | None = None,
        until: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict:
        """GET /v1/whatsapp/messages — workspace messages, newest first."""
        return self.client.get(
            "whatsapp/messages",
            params=_omit_none(
                {
                    "conversation_id": conversation_id,
                    "message_type": message_type,
                    "status": status,
                    "direction": direction,
                    "since": since,
                    "until": until,
                    "limit": limit,
                    "offset": offset,
                }
            )
            or None,
        )

    def get_status(self, message_id: str) -> dict:
        """GET /v1/whatsapp/messages/{message_id} — delivery status and paired reply."""
        return self.client.get(f"whatsapp/messages/{message_id}")

    def send_read_receipt(self, message_id: str) -> dict:
        """POST /v1/whatsapp/messages/{message_id}/read — WhatsApp blue ticks."""
        return self.client.post(f"whatsapp/messages/{message_id}/read")

    # --- Senders & templates ---

    def list_senders(
        self,
        *,
        is_active: bool | None = None,
        is_default: bool | None = None,
    ) -> dict:
        """GET /v1/whatsapp/senders — sender numbers in this workspace."""
        return self.client.get(
            "whatsapp/senders",
            params=_omit_none(
                {
                    "is_active": _bool_query(is_active),
                    "is_default": _bool_query(is_default),
                }
            )
            or None,
        )

    def get_sender(self, sender_id: str) -> dict:
        """GET /v1/whatsapp/senders/{sender_id}"""
        return self.client.get(f"whatsapp/senders/{sender_id}")

    def list_templates(
        self,
        *,
        sender_id: str | None = None,
        status: str | list[str] | None = None,
        category: str | list[str] | None = None,
        language: str | list[str] | None = None,
        name_or_content: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        sort: str | None = None,
    ) -> dict:
        """
        GET /v1/whatsapp/templates — cursor-paginated.

        ``status``, ``category``, and ``language`` may be repeated (OR).
        Only APPROVED templates can be sent.
        """
        return self.client.get(
            "whatsapp/templates",
            params=_omit_none(
                {
                    "sender_id": sender_id,
                    "status": status,
                    "category": category,
                    "language": language,
                    "name_or_content": name_or_content,
                    "cursor": cursor,
                    "limit": limit,
                    "sort": sort,
                }
            )
            or None,
        )

    def get_template(self, template_id: str) -> dict:
        """GET /v1/whatsapp/templates/{template_id}"""
        return self.client.get(f"whatsapp/templates/{template_id}")
