# Briq Python Client API Reference

Complete reference for all public classes and methods.

## Table of Contents

- [Client](#client)
- [Config](#config)
- [MetaAPI](#metaapi)
- [WorkspaceAPI](#workspaceapi)
- [CampaignAPI](#campaignapi)
- [MessageAPI](#messageapi)
- [DeveloperAppsAPI](#developerappsapi)
- [OtpAPI](#otpapi)
- [VoiceAPI](#voiceapi)
- [WebhooksAPI](#webhooksapi)
- [WhatsAppAPI](#whatsappapi)
- [Exceptions](#exceptions)

---

## Client

Main entry point for interacting with the Briq API.

### Constructor

```python
Client(api_key=None, base_url=None)
```

| Parameter  | Type  | Description                                                         |
|------------|-------|---------------------------------------------------------------------|
| `api_key`  | `str` | API key. Falls back to `BRIQ_API_KEY` env var then `.env` file.    |
| `base_url` | `str` | Base URL. Falls back to `BRIQ_BASE_URL` or `http://karibu.briq.tz`.|

### Attributes

| Attribute           | Type                | Description                         |
|---------------------|---------------------|-------------------------------------|
| `config`            | `Config`            | Configuration for this client       |
| `meta`              | `MetaAPI`           | Meta / health-check endpoints       |
| `workspace`         | `WorkspaceAPI`      | Workspace management                |
| `campaign`          | `CampaignAPI`       | Campaign management                 |
| `message`           | `MessageAPI`        | Message sending and history         |
| `developer_apps`    | `DeveloperAppsAPI`  | Developer app management (Bearer)   |
| `otp`               | `OtpAPI`            | OTP request / verify                |
| `voice`             | `VoiceAPI`          | Voice call initiation               |
| `webhooks`          | `WebhooksAPI`       | Webhook management                  |
| `whatsapp`          | `WhatsAppAPI`       | Karibu WhatsApp                     |

### Methods

#### login

```python
login(username, password) -> dict
```

Authenticate with OAuth2 password flow. On success stores the token in `client.config.access_token`; required before calling `developer_apps` endpoints.

| Parameter  | Type  |
|------------|-------|
| `username` | `str` |
| `password` | `str` |

**Returns:** `dict` — token response including `access_token` and `token_type`.  
**Raises:** `BriqAuthError`, `BriqRequestError`

#### request

```python
request(method, endpoint, data=None, params=None,
        prefix="v1", auth="api_key",
        extra_headers=None, files=None) -> dict
```

Low-level request method used internally by all sub-API classes.

| Parameter       | Type   | Default      | Description                                          |
|-----------------|--------|--------------|------------------------------------------------------|
| `method`        | `str`  | —            | HTTP method: `GET`, `POST`, `PATCH`, `DELETE`        |
| `endpoint`      | `str`  | —            | Path relative to `prefix`                            |
| `data`          | `dict` | `None`       | JSON request body (or form fields when using `files`)|
| `params`        | `dict` | `None`       | Query parameters                                     |
| `prefix`        | `str`  | `"v1"`       | URL prefix; use `""` for root / non-versioned paths  |
| `auth`          | `str`  | `"api_key"`  | `"api_key"`, `"bearer"`, or `"none"`                 |
| `extra_headers` | `dict` | `None`       | Additional headers merged into the request           |
| `files`         | `dict` | `None`       | Files for multipart upload (removes `Content-Type`)  |

**Returns:** `dict` — parsed JSON body, or `{}` for 204 responses.  
**Raises:** `BriqAuthError`, `BriqValidationError`, `BriqAPIError`, `BriqRequestError`

#### get

```python
get(endpoint, params=None, prefix="v1", auth="api_key", extra_headers=None) -> dict
```

Convenience wrapper for GET requests.

#### post

```python
post(endpoint, data=None, prefix="v1", auth="api_key",
     extra_headers=None, files=None) -> dict
```

Convenience wrapper for POST requests.

#### patch

```python
patch(endpoint, data=None, prefix="v1", auth="api_key", extra_headers=None) -> dict
```

Convenience wrapper for PATCH requests.

#### delete

```python
delete(endpoint, prefix="v1", auth="api_key", extra_headers=None) -> dict
```

Convenience wrapper for DELETE requests.

#### set_api_key

```python
set_api_key(api_key) -> None
```

Update the API key. Equivalent to `client.config.api_key = api_key`.

---

## Config

Manages runtime configuration.

### Constructor

```python
Config(api_key=None, base_url=None)
```

Loads `.env` from the current directory automatically.

### Properties

| Property       | Type           | Description                                                 |
|----------------|----------------|-------------------------------------------------------------|
| `api_key`      | `str \| None`  | Read/write. API key for `X-API-Key` header.                 |
| `base_url`     | `str`          | Read/write. Base URL for all requests.                      |
| `access_token` | `str \| None`  | Read/write. OAuth2 Bearer token; set automatically by `login()`. |
| `headers`      | `dict`         | Read-only. Returns `{"X-API-Key": ..., "Content-Type": "application/json"}`. Raises `ValueError` if `api_key` is not set. |

---

## MetaAPI

`client.meta`

No authentication required for `hello` and `get_version`.

### Methods

#### hello

```python
hello() -> dict
```

`GET /` — health check / landing page info.

#### get_version

```python
get_version() -> dict
```

`GET /version` — API version and deployment information.

#### developer_stats

```python
developer_stats() -> dict
```

`GET /karibu/x-api-key` — verify API key and return developer statistics. Requires `api_key` auth.

---

## WorkspaceAPI

`client.workspace`

### Methods

#### create

```python
create(name, description=None, developer_access=False) -> dict
```

`POST /v1/workspace/create/`

| Parameter          | Type   | Default | Description                          |
|--------------------|--------|---------|--------------------------------------|
| `name`             | `str`  | —       | Workspace name                       |
| `description`      | `str`  | `None`  | Optional description                 |
| `developer_access` | `bool` | `False` | Enable developer access for the workspace |

#### list

```python
list() -> dict
```

`GET /v1/workspace/all/`

#### get

```python
get(workspace_id) -> dict
```

`GET /v1/workspace/{workspace_id}`

#### update

```python
update(workspace_id, name=None, description=None, developer_access=None) -> dict
```

`PATCH /v1/workspace/update/{workspace_id}` — only supplied fields are updated.

---

## CampaignAPI

`client.campaign`

### Methods

#### create

```python
create(workspace_id, name, description=None, launch_date=None) -> dict
```

`POST /v1/campaign/create/`

| Parameter      | Type  | Description                            |
|----------------|-------|----------------------------------------|
| `workspace_id` | `str` | Workspace to create the campaign in    |
| `name`         | `str` | Campaign name                          |
| `description`  | `str` | Optional description                   |
| `launch_date`  | `str` | ISO 8601 datetime (e.g. `"2025-12-01T00:00:00"`) |

#### list

```python
list() -> dict
```

`GET /v1/campaign/all/`

#### get

```python
get(campaign_id) -> dict
```

`GET /v1/campaign/{campaign_id}/`

#### update

```python
update(campaign_id, name=None, description=None, launch_date=None) -> dict
```

`PATCH /v1/campaign/update/{campaign_id}` — only supplied fields are updated.

---

## MessageAPI

`client.message`

### Methods

#### send_instant

```python
send_instant(content, recipients, sender_id,
             campaign_id=None, groups=None, flash=False,
             send_at=None, app_id=None) -> dict
```

`POST /v1/message/send-instant`

| Parameter     | Type         | Default | Description                                              |
|---------------|--------------|---------|----------------------------------------------------------|
| `content`     | `str`        | —       | Message text                                             |
| `recipients`  | `list[str]`  | —       | Phone numbers                                            |
| `sender_id`   | `str`        | —       | Registered sender ID (2–13 characters)                   |
| `campaign_id` | `str`        | `None`  | Associate with a campaign                                |
| `groups`      | `list[str]`  | `None`  | Also send to these contact group IDs                     |
| `flash`       | `bool`       | `False` | Send as a flash message                                  |
| `send_at`     | `str`        | `None`  | ISO 8601 UTC schedule time (e.g. `"2025-12-01T10:00:00Z"`) |
| `app_id`      | `str`        | `None`  | Developer app ID — passed as `X-App-ID` header           |

**Returns:** `dict` — includes `job_id`, `status`, `message`, `stats`, `meta`.

#### send_campaign

```python
send_campaign(campaign_id, content, sender_id,
              start_date=None, end_date=None,
              frequency=None, app_id=None) -> dict
```

`POST /v1/message/send-campaign` — send to all contacts in a campaign.

| Parameter     | Type  | Default | Description                                              |
|---------------|-------|---------|----------------------------------------------------------|
| `campaign_id` | `str` | —       | Campaign ID                                              |
| `content`     | `str` | —       | Message text                                             |
| `sender_id`   | `str` | —       | Registered sender ID (2–13 characters)                   |
| `start_date`  | `str` | `None`  | ISO 8601 datetime for when sending starts                |
| `end_date`    | `str` | `None`  | ISO 8601 datetime for when sending ends                  |
| `frequency`   | `str` | `None`  | One of `once`, `hourly`, `daily`, `weekly`, `monthly`   |
| `app_id`      | `str` | `None`  | Developer app ID — passed as `X-App-ID` header           |

#### get_logs

```python
get_logs() -> dict
```

`GET /v1/message/logs`

#### get_history

```python
get_history() -> dict
```

`GET /v1/message/history`

#### get_history_by_recipient

```python
get_history_by_recipient(recipient) -> dict
```

`GET /v1/message/history/recipient/{recipient}`

| Parameter   | Type  | Description        |
|-------------|-------|--------------------|
| `recipient` | `str` | Recipient phone number |

#### get_message_log

```python
get_message_log(message_id) -> dict
```

`GET /v1/message/message-log/{message_id}`

---

## DeveloperAppsAPI

`client.developer_apps`

All methods require Bearer auth. Call `client.login()` before using.

### Methods

#### list

```python
list() -> dict
```

`GET /developer-apps/`

#### create

```python
create(app_name, app_description=None, workspace_id=None) -> dict
```

`POST /developer-apps/`

#### get

```python
get(app_id) -> dict
```

`GET /developer-apps/{app_id}`

#### get_by_key

```python
get_by_key(app_key) -> dict
```

`GET /developer-apps/by-key/{app_key}`

#### update

```python
update(app_id, app_name=None, app_description=None, workspace_id=None) -> dict
```

`PATCH /developer-apps/{app_id}` — only supplied fields are updated.

#### delete

```python
delete(app_id) -> dict
```

`DELETE /developer-apps/{app_id}` — returns `{}` on success (204).

#### list_by_workspace

```python
list_by_workspace(workspace_id) -> dict
```

`GET /workspaces/{workspace_id}/developer-apps`

#### transfer

```python
transfer(app_id, workspace_id) -> dict
```

`POST /developer-apps/{app_id}/transfer` — move app to another workspace.

#### attach_api_key

```python
attach_api_key(app_id, api_key_id) -> dict
```

`POST /developer-apps/{app_id}/api-keys/{api_key_id}/attach`

#### stats

```python
stats(app_id) -> dict
```

`GET /developer-apps/{app_id}/stats`

#### list_api_keys

```python
list_api_keys(app_id) -> dict
```

`GET /developer-apps/{app_id}/api-keys`

---

## OtpAPI

`client.otp`

### Methods

#### request

```python
request(phone_number, app_key, sender_id=None,
        otp_length=6, minutes_to_expire=10,
        delivery_method="sms", message_template=None) -> dict
```

`POST /v1/otp/request`

| Parameter           | Type  | Default  | Description                                    |
|---------------------|-------|----------|------------------------------------------------|
| `phone_number`      | `str` | —        | Recipient phone number                         |
| `app_key`           | `str` | —        | Developer app key                              |
| `sender_id`         | `str` | `None`   | SMS sender ID (defaults to "BRIQ OTP")         |
| `otp_length`        | `int` | `6`      | OTP code length                                |
| `minutes_to_expire` | `int` | `10`     | Expiry in minutes                              |
| `delivery_method`   | `str` | `"sms"`  | `"sms"` or `"call"`                            |
| `message_template`  | `str` | `None`   | Custom template — use `{code}` as placeholder  |

#### verify

```python
verify(phone_number, app_key, code) -> dict
```

`POST /v1/otp/verify`

#### resend

```python
resend(phone_number, app_key, sender_id=None,
       otp_length=6, minutes_to_expire=10,
       delivery_method="sms", message_template=None) -> dict
```

`POST /v1/otp/resend` — same parameters as `request`.

#### invalidate

```python
invalidate(phone_number, app_key) -> dict
```

`POST /v1/otp/invalidate` — cancel any active OTP for the phone number.

#### status

```python
status(phone_number, app_key) -> dict
```

`GET /v1/otp/status`

---

## VoiceAPI

`client.voice`

### Methods

#### call_audio

```python
call_audio(receiver_number, audio_url) -> dict
```

`POST /v1/voice/calls/audio` — initiate a call that plays audio from a public URL (MP3 or WAV).

#### call_audio_upload

```python
call_audio_upload(receiver_number, file) -> dict
```

`POST /v1/voice/calls/audio/upload` — upload a local audio file (MP3 or WAV) and initiate a call. `file` must be an open binary file-like object.

#### call_tts

```python
call_tts(receiver_number, text) -> dict
```

`POST /v1/voice/calls/tts` — initiate a call that reads `text` to the recipient via text-to-speech.

---

## WebhooksAPI

`client.webhooks`

### Methods

#### create

```python
create(app_id, service_type, url, secret_token=None) -> dict
```

`POST /v1/webhooks/`

| Parameter      | Type  | Description                                            |
|----------------|-------|--------------------------------------------------------|
| `app_id`       | `str` | Developer app UUID                                     |
| `service_type` | `str` | One of `sms`, `voice`, `otp`, `whatsapp`, `email`     |
| `url`          | `str` | Endpoint that will receive webhook events              |
| `secret_token` | `str` | Signing secret — minimum 16 characters (optional)      |

**Note:** `secret_token` may be masked in responses.

#### list

```python
list() -> dict
```

`GET /v1/webhooks/all`

#### list_by_app

```python
list_by_app(app_id) -> dict
```

`GET /v1/webhooks/app/{app_id}`

#### get

```python
get(webhook_id) -> dict
```

`GET /v1/webhooks/{webhook_id}`

#### update

```python
update(webhook_id, service_type=None, url=None, secret_token=None) -> dict
```

`PATCH /v1/webhooks/{webhook_id}` — only supplied fields are updated.

#### delete

```python
delete(webhook_id) -> dict
```

`DELETE /v1/webhooks/{webhook_id}` — returns `{}` on success (204).

---

## WhatsAppAPI

`client.whatsapp`

Karibu WhatsApp helpers map 1:1 to the documented conversations, messages,
senders, and templates routes. Inbound events stay on `client.webhooks` with
`service_type="whatsapp"`.

Text / media / interactive sends need an open 24-hour window. A closed window is
`422 WINDOW_CLOSED` and is raised as `BriqAPIError` with `.code == "WINDOW_CLOSED"`.
Templates always send and reopen the window.

Media limits (optional `size_bytes` is checked client-side before the request):

| Kind | Limit |
|------|-------|
| image | 5 MB |
| video | 16 MB |
| audio | 16 MB |
| document | 100 MB |

### Conversations

#### list_conversations

```python
list_conversations(sender=None, sender_id=None, recipient=None, status=None,
                   search=None, since=None, limit=None, offset=None) -> dict
```

`GET /v1/whatsapp/conversations`

#### get_conversation

```python
get_conversation(conversation_id) -> dict
```

`GET /v1/whatsapp/conversations/{conversation_id}`

#### inbox_summary

```python
inbox_summary(sender=None, sender_id=None) -> dict
```

`GET /v1/whatsapp/conversations/summary`

#### mark_read

```python
mark_read(conversation_id, up_to=None) -> dict
```

`POST /v1/whatsapp/conversations/{conversation_id}/read` — inbox unread state, not a WhatsApp read receipt.

#### delete_conversation

```python
delete_conversation(conversation_id) -> dict
```

`DELETE /v1/whatsapp/conversations/{conversation_id}`

### Messages

Target with `to` + optional `sender`, or `conversation_id`.

#### send_text

```python
send_text(body, to=None, sender=None, conversation_id=None, sender_id=None) -> dict
```

`POST /v1/whatsapp/messages/text`

#### send_template

```python
send_template(template_name, to=None, sender=None, conversation_id=None,
              sender_id=None, variables=None) -> dict
```

`POST /v1/whatsapp/messages/template`

#### send_image / send_video / send_document / send_audio

```python
send_image(..., media_url=None, file_id=None, caption=None, size_bytes=None)
send_video(..., media_url=None, file_id=None, caption=None, size_bytes=None)
send_document(..., media_url=None, file_id=None, caption=None, filename=None, size_bytes=None)
send_audio(..., media_url=None, file_id=None, size_bytes=None)
```

`POST /v1/whatsapp/messages/{image,video,document,audio}`

#### send_interactive

```python
send_interactive(interactive, to=None, sender=None, conversation_id=None, sender_id=None) -> dict
```

`POST /v1/whatsapp/messages/interactive` — pass a WhatsApp `interactive` object (`type` required).

#### list_messages

```python
list_messages(conversation_id=None, message_type=None, status=None, direction=None,
              since=None, until=None, limit=None, offset=None) -> dict
```

`GET /v1/whatsapp/messages`

#### get_status

```python
get_status(message_id) -> dict
```

`GET /v1/whatsapp/messages/{message_id}`

#### send_read_receipt

```python
send_read_receipt(message_id) -> dict
```

`POST /v1/whatsapp/messages/{message_id}/read`

### Senders and templates

#### list_senders / get_sender

```python
list_senders(is_active=None, is_default=None) -> dict
get_sender(sender_id) -> dict
```

`GET /v1/whatsapp/senders` — these routes return the data shape directly (not the send envelope).

#### list_templates / get_template

```python
list_templates(sender_id=None, status=None, category=None, language=None,
               name_or_content=None, cursor=None, limit=None, sort=None) -> dict
get_template(template_id) -> dict
```

`GET /v1/whatsapp/templates` — `status` / `category` / `language` may be a string or list (OR).

---

## Exceptions

All exceptions live in `briq.exceptions` and inherit from `BriqError`.

```python
from briq.exceptions import (
    BriqError,
    BriqAuthError,
    BriqAPIError,
    BriqRequestError,
    BriqConfigError,
    BriqValidationError,
)
```

| Exception             | HTTP Status | Description                                              |
|-----------------------|-------------|----------------------------------------------------------|
| `BriqError`           | —           | Base class for all Briq exceptions                       |
| `BriqAuthError`       | 401         | Authentication failed — invalid or missing credentials   |
| `BriqValidationError` | 422         | Field-level validation failure; see `.detail` below      |
| `BriqAPIError`        | 400 / other | API returned an error. Envelope bodies set `.code`, `.errors`, `.request_id`, `.status_code` |
| `BriqRequestError`    | —           | Network or transport failure                             |
| `BriqConfigError`     | —           | Configuration problem (e.g. missing API key)             |

### BriqValidationError

```python
class BriqAPIError(BriqError):
    status_code: int | None
    code: str | None          # errors[0].code from a Karibu envelope
    errors: list              # envelope errors array
    request_id: str | None
    data: dict | None
    body: dict | list | None
```

```python
class BriqValidationError(BriqError):
    detail: list  # field-level error dicts from the 422 response body
```

```python
try:
    client.message.send_instant(content="", recipients=[], sender_id="X")
except BriqValidationError as e:
    print(e)         # human-readable summary
    print(e.detail)  # list of {"loc": [...], "msg": "...", "type": "..."} dicts
```
