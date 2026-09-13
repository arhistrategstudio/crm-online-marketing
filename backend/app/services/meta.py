"""Helpers for the Meta (Facebook/Instagram) Lead Ads webhook integration."""

import hashlib
import hmac

import requests

GRAPH_API_BASE = "https://graph.facebook.com"

# Common field names used across Meta Lead Ads forms; the first match wins.
NAME_FIELDS = ("full_name", "first_name")
EMAIL_FIELDS = ("email",)
PHONE_FIELDS = ("phone_number", "phone")


def verify_signature(raw_body: bytes, signature_header: str | None, app_secret: str) -> bool:
    """Checks the `X-Hub-Signature-256` header Meta sends with every webhook POST."""
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    expected = hmac.new(app_secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    provided = signature_header.removeprefix("sha256=")
    return hmac.compare_digest(expected, provided)


def fetch_lead_data(leadgen_id: str, access_token: str, api_version: str) -> dict:
    """Retrieves the full lead (name/email/phone/platform/...) for a leadgen_id from the Graph API.

    The webhook payload only carries the leadgen_id; the actual submitted answers
    must be fetched separately using a Page access token with `leads_retrieval`.
    `platform` must be requested explicitly (it's not returned by default) — it's how we
    tell Facebook and Instagram lead ads apart, since both fire the same `leadgen` webhook
    on the connected Facebook Page.
    """
    url = f"{GRAPH_API_BASE}/{api_version}/{leadgen_id}"
    params = {"access_token": access_token, "fields": "field_data,platform,ad_id,form_id,created_time"}
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def detect_platform(lead_data: dict) -> str:
    """Maps the Graph API `platform` field ("ig"/"fb") onto our Channel values.

    Falls back to "facebook" when the field is missing (older API versions, or a lead
    ad running only on Facebook) rather than guessing.
    """
    platform = (lead_data.get("platform") or "").lower()
    return "instagram" if platform == "ig" else "facebook"


def extract_contact_fields(lead_data: dict) -> dict[str, str | None]:
    """Maps Meta's `field_data` list onto the name/email/phone fields our Contact model needs."""
    values: dict[str, str] = {}
    for entry in lead_data.get("field_data", []):
        field_name = entry.get("name")
        field_values = entry.get("values") or []
        if field_name and field_values:
            values[field_name] = field_values[0]

    name = next((values[key] for key in NAME_FIELDS if values.get(key)), None)
    if not name and values.get("first_name"):
        name = f"{values['first_name']} {values.get('last_name', '')}".strip()

    return {
        "name": name or "Meta lead",
        "email": next((values[key] for key in EMAIL_FIELDS if values.get(key)), None),
        "phone": next((values[key] for key in PHONE_FIELDS if values.get(key)), None),
    }
