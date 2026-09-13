"""Helpers for the Viber Bot API integration.

Separate ecosystem from Meta — Viber has its own REST API (chatapi.viber.com) authenticated
with a single "Auth Token" for a Public Account/bot, not OAuth. Requires the account owner to
create a Public Account via the Viber app and generate the token at partners.viber.com.
"""

import hashlib
import hmac

import requests

VIBER_API_BASE = "https://chatapi.viber.com/pa"


def verify_signature(raw_body: bytes, signature_header: str | None, auth_token: str) -> bool:
    """Checks the `X-Viber-Content-Signature` header Viber sends with every webhook POST."""
    if not signature_header:
        return False
    expected = hmac.new(auth_token.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_header)


def send_message(receiver_id: str, text: str, auth_token: str, sender_name: str = "CRM Online Marketing") -> dict:
    """Sends a text message to a Viber user. Viber only allows this after the user has messaged the bot first."""
    response = requests.post(
        f"{VIBER_API_BASE}/send_message",
        json={"receiver": receiver_id, "type": "text", "text": text, "sender": {"name": sender_name}},
        headers={"X-Viber-Auth-Token": auth_token},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def set_webhook(url: str, auth_token: str) -> dict:
    """One-time registration of our webhook URL with Viber. Not called automatically — run manually once
    a real Auth Token is configured (see docs/integrations.md)."""
    response = requests.post(
        f"{VIBER_API_BASE}/set_webhook",
        json={"url": url, "event_types": ["message", "conversation_started", "subscribed", "unsubscribed"]},
        headers={"X-Viber-Auth-Token": auth_token},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()
