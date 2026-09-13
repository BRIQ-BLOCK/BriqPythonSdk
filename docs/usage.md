# Briq Python Client Usage Guide

This guide covers everything you need to use the Briq Python client library.

## Table of Contents

- [Installation](#installation)
- [Requirements](#requirements)
- [Environment Variables](#environment-variables)
- [Client Initialization](#client-initialization)
- [Authentication](#authentication)
  - [API Key (default)](#api-key-default)
  - [OAuth2 Bearer — Developer Apps](#oauth2-bearer--developer-apps)
- [Meta](#meta)
- [Workspace Management](#workspace-management)
- [Campaign Management](#campaign-management)
- [Message Management](#message-management)
- [Developer Apps](#developer-apps)
- [OTP](#otp)
- [Voice Calls](#voice-calls)
- [Webhooks](#webhooks)
- [Karibu Email](#karibu-email)
- [Error Handling](#error-handling)

---

## Installation

```bash
pip install briq
```

## Requirements

- Python 3.10+
- `requests`
- `python-dotenv`

---

## Environment Variables

| Variable        | Required | Description                                              |
|-----------------|----------|----------------------------------------------------------|
| `BRIQ_API_KEY`  | Yes      | Your Briq API key (used by all standard endpoints)       |
| `BRIQ_BASE_URL` | No       | Override the default base URL (`http://karibu.briq.tz`)  |

Set them in your shell:

```bash
export BRIQ_API_KEY=your_api_key_here
export BRIQ_BASE_URL=http://karibu.briq.tz   # optional
```

Or place them in a `.env` file at your project root — the library loads it automatically:

```
BRIQ_API_KEY=your_api_key_here
BRIQ_BASE_URL=http://karibu.briq.tz
```

---

## Client Initialization

```python
import briq

# Reads BRIQ_API_KEY / BRIQ_BASE_URL from environment or .env
client = briq.Client()

# Explicit values
client = briq.Client(
    api_key="your_api_key_here",
    base_url="http://karibu.briq.tz",
)
```

After initialization the client exposes these sub-APIs:

| Attribute           | Class               |
|---------------------|---------------------|
| `client.meta`       | `MetaAPI`           |
| `client.workspace`  | `WorkspaceAPI`      |
| `client.campaign`   | `CampaignAPI`       |
| `client.message`    | `MessageAPI`        |
| `client.developer_apps` | `DeveloperAppsAPI` |
| `client.otp`        | `OtpAPI`            |
| `client.voice`      | `VoiceAPI`          |
| `client.webhooks`   | `WebhooksAPI`       |
| `client.email`      | `EmailAPI`          |

---

## Authentication

### API Key (default)

Most endpoints authenticate via `X-API-Key` header using the key stored in `client.config.api_key`. No extra setup is needed beyond setting `BRIQ_API_KEY`.

You can update the key at runtime:

```python
client.set_api_key("new_api_key")
# or equivalently:
client.config.api_key = "new_api_key"
```

### OAuth2 Bearer — Developer Apps

`DeveloperAppsAPI` endpoints require a Bearer token obtained by calling `client.login()`:

```python
token_data = client.login(username="user@example.com", password="secret")
# The access token is stored automatically in client.config.access_token
```

After a successful login every `developer_apps` call uses the stored token transparently. The token is not persisted across process restarts; call `login()` again in each new session.

---

## Meta

```python
# GET / — landing page / health check (no auth required)
info = client.meta.hello()

# GET /version — API version and deployment info (no auth required)
version = client.meta.get_version()
print(version)

# GET /karibu/x-api-key — verify API key, return developer stats
stats = client.meta.developer_stats()
print(stats)
```

---

## Workspace Management

### Create a Workspace

```python
workspace = client.workspace.create(
    name="Marketing",
    description="Main marketing workspace",
    developer_access=True,   # optional, default False
)
```

### List All Workspaces

```python
workspaces = client.workspace.list()
```

### Get a Workspace

```python
workspace = client.workspace.get("workspace-uuid")
```

### Update a Workspace

```python
updated = client.workspace.update(
    "workspace-uuid",
    name="New Name",
    description="Updated description",
    developer_access=False,  # optional
)
```

---

## Campaign Management

### Create a Campaign

```python
campaign = client.campaign.create(
    workspace_id="workspace-uuid",
    name="Product Launch",
    description="Q4 product launch campaign",
    launch_date="2025-12-01T00:00:00",  # ISO 8601
)
```

### List All Campaigns

```python
campaigns = client.campaign.list()
```

### Get a Campaign

```python
campaign = client.campaign.get("campaign-uuid")
```

### Update a Campaign

```python
updated = client.campaign.update(
    "campaign-uuid",
    name="Renamed Campaign",
    launch_date="2025-12-15T00:00:00",
)
```

---

## Message Management

### Send an Instant Message

```python
result = client.message.send_instant(
    content="Hello from Briq!",
    recipients=["255788344348", "255712345678"],
    sender_id="COMPANY",
    campaign_id="campaign-uuid",    # optional
    groups=["group-uuid"],          # optional — also send to contact groups
    flash=False,                    # optional — flash SMS
    send_at="2025-12-01T10:00:00Z", # optional — schedule (ISO 8601 UTC)
    app_id="developer-app-uuid",    # optional — app for webhook delivery
)
print(result)
```

### Send a Campaign Message

Sends to all contacts in a campaign. Note: there is no `group_id` parameter here.

```python
result = client.message.send_campaign(
    campaign_id="campaign-uuid",
    content="Campaign message content",
    sender_id="COMPANY",
    start_date="2025-12-01T08:00:00",   # optional
    end_date="2025-12-31T20:00:00",     # optional
    frequency="daily",                  # optional: once, hourly, daily, weekly, monthly
    app_id="developer-app-uuid",        # optional
)
print(result)
```

### Get Message Logs

```python
logs = client.message.get_logs()
print(logs)
```

### Get Message History

```python
history = client.message.get_history()
print(history)
```

### Get History by Recipient

```python
messages = client.message.get_history_by_recipient("+255788344348")
print(messages)
```

### Get a Specific Message Log

```python
detail = client.message.get_message_log("message-uuid")
print(detail)
```

---

## Developer Apps

These endpoints require Bearer auth — call `client.login()` first.

```python
client.login(username="user@example.com", password="secret")

# List apps
apps = client.developer_apps.list()

# Create an app
app = client.developer_apps.create(
    app_name="My App",
    app_description="Integration app",
    workspace_id="workspace-uuid",  # optional
)

# Get by ID
app = client.developer_apps.get("app-uuid")

# Get by app_key
app = client.developer_apps.get_by_key("app-key-string")

# Update
updated = client.developer_apps.update(
    "app-uuid",
    app_name="Renamed App",
    workspace_id="new-workspace-uuid",
)

# Delete
client.developer_apps.delete("app-uuid")

# List apps in a workspace
apps = client.developer_apps.list_by_workspace("workspace-uuid")

# Transfer app to another workspace
client.developer_apps.transfer("app-uuid", "target-workspace-uuid")

# Attach an API key to an app
client.developer_apps.attach_api_key("app-uuid", "api-key-uuid")

# Get app statistics
stats = client.developer_apps.stats("app-uuid")

# List API keys for an app
keys = client.developer_apps.list_api_keys("app-uuid")
```

---

## OTP

```python
# Request an OTP
result = client.otp.request(
    phone_number="+255712345678",
    app_key="your-app-key",
    sender_id="MYAPP",              # optional
    otp_length=6,                   # optional, default 6
    minutes_to_expire=10,           # optional, default 10
    delivery_method="sms",          # optional: "sms" or "call"
    message_template="Your code is {code}",  # optional
)
print(result)

# Verify the OTP
result = client.otp.verify(
    phone_number="+255712345678",
    app_key="your-app-key",
    code="123456",
)
print(result)

# Resend an OTP
result = client.otp.resend(
    phone_number="+255712345678",
    app_key="your-app-key",
)

# Check OTP status
status = client.otp.status(
    phone_number="+255712345678",
    app_key="your-app-key",
)

# Invalidate active OTP
client.otp.invalidate(
    phone_number="+255712345678",
    app_key="your-app-key",
)
```

---

## Voice Calls

### Call Using a URL

```python
result = client.voice.call_audio(
    receiver_number="255788344348",
    audio_url="https://example.com/audio.mp3",
)
print(result)
```

### Call With a File Upload

```python
with open("audio.mp3", "rb") as f:
    result = client.voice.call_audio_upload(
        receiver_number="255788344348",
        file=f,
    )
print(result)
```

### Call With Text-to-Speech

```python
result = client.voice.call_tts(
    receiver_number="255788344348",
    text="Hello, your order has been confirmed.",
)
print(result)
```

---

## Webhooks

```python
# Create a webhook
webhook = client.webhooks.create(
    app_id="developer-app-uuid",
    service_type="sms",             # sms, voice, otp, whatsapp, email
    url="https://your-app.example.com/webhook",
    secret_token="your_secret_min16chars",  # optional, min 16 chars
)
print(webhook)

# List all webhooks
webhooks = client.webhooks.list()

# List webhooks for a specific app
webhooks = client.webhooks.list_by_app("developer-app-uuid")

# Get a webhook by ID
webhook = client.webhooks.get("webhook-uuid")

# Update a webhook
updated = client.webhooks.update(
    "webhook-uuid",
    url="https://new-url.example.com/webhook",
    secret_token="new_secret_token_min16chars",
)

# Delete a webhook
client.webhooks.delete("webhook-uuid")
```

Email delivery events use the existing webhooks API with `service_type="email"`. There is no separate email webhook client.

---

## Karibu Email

`client.email` covers the documented Karibu Email surfaces
([docs](https://docs.briq.tz/Karibu-Email/index.md)). There is no attachment-send API.

```python
# Sender profiles (read-only; created in the dashboard)
senders = client.email.list_senders()
profile = client.email.get_sender("sender-profile-uuid")

# Preflight — nothing queued or charged
check = client.email.validate(
    to=["asha@example.com"],
    subject="Your receipt",
    text="Thanks. Your order is paid.",
)
if not check["data"]["can_send"]:
    raise SystemExit(check["data"]["errors"])

# Transactional send. Idempotency-Key is generated if omitted.
accepted = client.email.send_messages(
    messages=[
        {
            "to": "asha@example.com",
            "subject": "Your receipt #10421",
            "text": "Thanks. Your order is paid.",
        }
    ],
    transactional=True,
    idempotency_key="order-10421",  # optional; reused on 503 SEND_FAILED
)
job_id = accepted["data"]["job_id"]

# Broadcast (no transactional flag)
client.email.send_broadcast(
    subject="We open at 08:00 on Saturday",
    group_ids=["contact-group-uuid"],
    text="Come by any time before noon.",
)

# Track
client.email.list_messages(job_id=job_id, status="sent")
client.email.get_message("message-uuid")
client.email.retry_messages(["message-uuid"])

# Jobs
client.email.get_job(job_id)
client.email.list_scheduled_jobs()
client.email.cancel_job(job_id)
# Optional helper: poll until queued/scheduled are absent from counts
client.email.wait_job(job_id, timeout=30, interval=1)
```

Envelope failures raise `BriqAPIError` with `.code`, `.errors`, and `.request_id`.
The client retries only documented `503 SEND_FAILED` / `SEND_ALLOWED` on
`send_messages`, always with the same idempotency key.

---

## Error Handling

```python
import briq
from briq.exceptions import (
    BriqAuthError,
    BriqAPIError,
    BriqRequestError,
    BriqConfigError,
    BriqValidationError,
)

try:
    client = briq.Client()
    result = client.message.send_instant(
        content="Hello!",
        recipients=["255788344348"],
        sender_id="TEST",
    )
except BriqAuthError as e:
    print(f"Authentication error: {e}")

except BriqValidationError as e:
    print(f"Validation error: {e}")
    # e.detail is a list of field-level error dicts from the API (422 response)
    for err in e.detail:
        print(err)

except BriqAPIError as e:
    print(f"API error: {e}")
    # Envelope failures (email and other Karibu envelope routes):
    print(e.code, e.request_id, e.errors)

except BriqRequestError as e:
    print(f"Network/transport error: {e}")

except BriqConfigError as e:
    print(f"Configuration error: {e}")
```

| Exception             | When raised                                              |
|-----------------------|----------------------------------------------------------|
| `BriqAuthError`       | 401 — invalid or missing API key / Bearer token          |
| `BriqValidationError` | 422 — field-level validation failure; `.detail` has info |
| `BriqAPIError`        | 400 or other HTTP error                                  |
| `BriqRequestError`    | Network / transport failure                              |
| `BriqConfigError`     | Missing required configuration (e.g. no API key set)    |
