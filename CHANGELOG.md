# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2026-09-13

Karibu Email (BRIQ-PILOt #691 / PR #1) and Karibu WhatsApp (BRIQ-PILOt #692 / PR #2)
on one client. SMS, OTP, voice, workspace, and campaign APIs are unchanged.

### Added

- `client.email` (Karibu Email) — documented senders, validate, messages,
  broadcasts, and jobs helpers:
  - `list_senders`, `get_sender`
  - `validate` (preflight; nothing queued or charged)
  - `send_messages` (1–500 individually addressed emails; `Idempotency-Key`;
    503 `SEND_FAILED` / `SEND_ALLOWED` retry)
  - `send_broadcast`
  - `list_messages`, `get_message`, `retry_messages`
  - `get_job`, `list_scheduled_jobs`, `cancel_job`, `wait_job`
- `client.whatsapp` (Karibu WhatsApp) — documented conversations, messages,
  senders, and templates helpers:
  - Conversations: `list_conversations`, `get_conversation`, `inbox_summary`,
    `mark_read`, `delete_conversation`
  - Messages: `send_text`, `send_template`, `send_image`, `send_video`,
    `send_document`, `send_audio`, `send_interactive`
  - Status: `list_messages`, `get_status`, `send_read_receipt`
  - Catalog: `list_senders`, `get_sender`, `list_templates`, `get_template`

### Changed

- HTTP layer identifies the SDK as `User-Agent: Briq-Python/{version}`.
- `BriqAPIError` exposes Karibu envelope fields: `.code`, `.errors`,
  `.request_id`, `.status_code`, and `.data` (Email codes such as
  `INSUFFICIENT_ALLOCATION`; WhatsApp `WINDOW_CLOSED`; and other documented
  envelope codes).
- Email `send_messages` always sends an `Idempotency-Key` (caller-supplied or
  generated UUID) and retries only documented `503 SEND_FAILED` /
  `SEND_ALLOWED`, reusing the same key.

### Notes

- SMS, OTP, voice, workspace, and campaign APIs are unchanged.
- No invented Email or WhatsApp endpoints; helpers map 1:1 to Karibu docs.
- Webhooks remain on `client.webhooks` (`service_type="email"` or
  `"whatsapp"`). There is no separate email or WhatsApp webhook client.

### Upgrade

```bash
pip install -U briq==0.3.0
```

[Unreleased]: https://github.com/BRIQ-BLOCK/BriqPythonSdk/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/BRIQ-BLOCK/BriqPythonSdk/compare/v0.2.0...v0.3.0
