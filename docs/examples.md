# Briq Python Client Examples

Practical, runnable examples for common Briq integration patterns.

## Basic Setup

```python
import briq

# Reads BRIQ_API_KEY (and optionally BRIQ_BASE_URL) from environment or .env
client = briq.Client()
```

---

## Workspace → Campaign → Message Flow

```python
import briq
from datetime import datetime, timedelta, timezone

client = briq.Client()

# 1. Create a workspace
workspace = client.workspace.create(
    name="Marketing Workspace",
    description="Workspace for marketing campaigns",
)
workspace_id = workspace["id"]
print("Workspace:", workspace)

# 2. Create a campaign in the workspace
launch_date = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
campaign = client.campaign.create(
    workspace_id=workspace_id,
    name="Product Launch Campaign",
    description="Campaign for new product launch",
    launch_date=launch_date,
)
campaign_id = campaign["id"]
print("Campaign:", campaign)

# 3. Send an instant message associated with the campaign
result = client.message.send_instant(
    content="We're excited to announce our new product launch!",
    recipients=["255788344348", "255712345678"],
    sender_id="COMPANY",
    campaign_id=campaign_id,
)
print("Send result:", result)

# 4. Send to all contacts in the campaign
campaign_send = client.message.send_campaign(
    campaign_id=campaign_id,
    content="Campaign broadcast content",
    sender_id="COMPANY",
    frequency="once",
)
print("Campaign send:", campaign_send)
```

---

## Error Handling

```python
import briq
from briq.exceptions import (
    BriqAuthError,
    BriqAPIError,
    BriqRequestError,
    BriqValidationError,
)

client = briq.Client()

try:
    result = client.message.send_instant(
        content="Hello!",
        recipients=["255788344348"],
        sender_id="TEST",
    )
    print(result)
except BriqAuthError as e:
    print(f"Auth error: {e}")
except BriqValidationError as e:
    print(f"Validation error: {e}")
    # e.detail contains field-level errors from the 422 response
    for err in e.detail:
        print(" ", err)
except BriqAPIError as e:
    print(f"API error: {e}")
except BriqRequestError as e:
    print(f"Network error: {e}")
```

---

## Login + Developer Apps

```python
import briq

client = briq.Client()

# Authenticate — stores Bearer token in client.config.access_token
client.login(username="user@example.com", password="secret")

# List all developer apps
apps = client.developer_apps.list()
print("Apps:", apps)

# Create a new app
app = client.developer_apps.create(
    app_name="SMS Notifier",
    app_description="App for delivery notifications",
)
print("Created app:", app)
```

---

## OTP Request and Verify

```python
import briq

client = briq.Client()
APP_KEY = "your-app-key"

# Request an OTP
result = client.otp.request(
    phone_number="+255712345678",
    app_key=APP_KEY,
    sender_id="MYAPP",
    otp_length=6,
    minutes_to_expire=10,
)
print("OTP request:", result)

# Verify the OTP (code entered by the user)
code = input("Enter OTP code: ")
verify = client.otp.verify(
    phone_number="+255712345678",
    app_key=APP_KEY,
    code=code,
)
print("Verify result:", verify)
```

---

## Voice Call — TTS

```python
import briq

client = briq.Client()

result = client.voice.call_tts(
    receiver_number="255788344348",
    text="Hello, your order has been confirmed and will arrive tomorrow.",
)
print(result)
```

## Voice Call — Audio URL

```python
import briq

client = briq.Client()

result = client.voice.call_audio(
    receiver_number="255788344348",
    audio_url="https://example.com/notification.mp3",
)
print(result)
```

## Voice Call — File Upload

```python
import briq

client = briq.Client()

with open("notification.mp3", "rb") as f:
    result = client.voice.call_audio_upload(
        receiver_number="255788344348",
        file=f,
    )
print(result)
```

---

## Webhooks — Create and List

```python
import briq

client = briq.Client()

# Create a webhook for an existing developer app
webhook = client.webhooks.create(
    app_id="developer-app-uuid",
    service_type="sms",
    url="https://your-app.example.com/webhook/sms",
    secret_token="supersecret_min_16_chars",
)
print("Created webhook:", webhook)

# List all webhooks
all_webhooks = client.webhooks.list()
print("All webhooks:", all_webhooks)

# List webhooks for a specific app
app_webhooks = client.webhooks.list_by_app("developer-app-uuid")
print("App webhooks:", app_webhooks)
```

---

## Scheduled Message

```python
import briq

client = briq.Client()

result = client.message.send_instant(
    content="Reminder: Your appointment is tomorrow at 10am.",
    recipients=["255788344348"],
    sender_id="CLINIC",
    send_at="2025-12-01T07:00:00Z",  # ISO 8601 UTC
)
print(result)
```

---

## Message History and Logs

```python
import briq

client = briq.Client()

# All message history
history = client.message.get_history()
print(history)

# History for a specific recipient
recipient_history = client.message.get_history_by_recipient("+255788344348")
print(recipient_history)

# All message logs
logs = client.message.get_logs()
print(logs)

# Detail for one message
detail = client.message.get_message_log("message-uuid")
print(detail)
```

---

## Karibu Email — Send and Track

```python
import briq
from briq.exceptions import BriqAPIError

client = briq.Client()

# Confirm a verified sender profile exists (created in the dashboard)
for profile in client.email.list_senders()["data"]["items"]:
    print(profile["sender_id"], profile["from_email"], profile["is_verified"])

preflight = client.email.validate(
    to=["asha@example.com", "juma@example.com"],
    subject="Your receipt from Duka la Asha",
    text="Thanks. Your order is paid.",
)
print(preflight["data"]["can_send"], preflight["data"]["emails_required"])

try:
    accepted = client.email.send_messages(
        messages=[
            {
                "to": "asha@example.com",
                "subject": "Your receipt #10421",
                "text": "Hi Asha, your order is paid.",
            }
        ],
        transactional=True,
        idempotency_key="order-10421",
    )
except BriqAPIError as e:
    # Envelope: branch on e.code (INSUFFICIENT_ALLOCATION, SENDER_UNVERIFIED, ...)
    print(e.code, e.request_id, e.errors)
    raise

job_id = accepted["data"]["job_id"]
print("queued", job_id, "replay", accepted["data"].get("idempotent_replay"))

# Optional: poll the job rollup until queued/scheduled drop out of counts
status = client.email.wait_job(job_id, timeout=30, interval=1)
print(status["data"]["counts"])

# Broadcast the same body to a saved contact group
client.email.send_broadcast(
    subject="We open at 08:00 on Saturday",
    group_ids=["contact-group-uuid"],
    html='<p style="font-family:Arial,sans-serif">Come by any time before noon.</p>',
)

# List failures and retry eligible ones (never re-charged)
failed = client.email.list_messages(status="failed", job_id=job_id)
ids = [row["message_id"] for row in failed["data"]["items"]]
if ids:
    client.email.retry_messages(ids)
```

Email webhooks (`email.sent`, `email.failed`, `email.bounced`) are registered with
the existing `client.webhooks` API (`service_type="email"`). There is no separate
email webhook client and no attachment-send helper.

---

## Karibu WhatsApp — Template, Reply, Track

```python
import briq
from briq.exceptions import BriqAPIError
from briq.whatsapp import WINDOW_CLOSED

client = briq.Client()

# Start or re-engage a conversation (always allowed)
queued = client.whatsapp.send_template(
    "order_update",
    to="255712345678",
    variables={"1": "A1234"},
)
print("queued", queued["data"]["message_id"])

# Free-form reply — needs an open 24-hour window
try:
    client.whatsapp.send_text(
        "Thanks, your order ships today.",
        to="255712345678",
    )
except BriqAPIError as e:
    if e.code == WINDOW_CLOSED:
        print("window closed; send a template instead")
    else:
        raise

# Media (image ≤5 MB; pass size_bytes to check before the request)
client.whatsapp.send_image(
    to="255712345678",
    media_url="https://example.com/receipt.jpg",
    caption="Your receipt",
)

# Inbox + catch-up without inventing a webhook client
print(client.whatsapp.inbox_summary()["data"])
inbound = client.whatsapp.list_messages(direction="inbound", limit=50)
print(inbound["data"]["items"])

status = client.whatsapp.get_status(queued["data"]["message_id"])
print(status["data"]["status"])
```

WhatsApp webhooks (`whatsapp.received`, conversation updates) are registered with
the existing `client.webhooks` API (`service_type="whatsapp"`).
