import hashlib
import hmac
import json

from app.config import Settings, get_settings
from app.main import app


def override_settings(anon_client, **overrides):
    base = Settings(_env_file=None)
    for key, value in overrides.items():
        setattr(base, key, value)
    app.dependency_overrides[get_settings] = lambda: base
    return base


LEADGEN_PAYLOAD = {
    "object": "page",
    "entry": [
        {
            "id": "123456",
            "time": 1700000000,
            "changes": [
                {
                    "field": "leadgen",
                    "value": {
                        "leadgen_id": "lg-1",
                        "page_id": "123456",
                        "form_id": "form-1",
                        "ad_id": "ad-1",
                        "created_time": 1700000000,
                    },
                }
            ],
        }
    ],
}


def sign(body: bytes, secret: str) -> str:
    return "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def test_verify_webhook_returns_challenge_on_match(anon_client):
    override_settings(anon_client, meta_verify_token="secret-token")

    response = anon_client.get(
        "/api/v1/webhooks/meta",
        params={"hub.mode": "subscribe", "hub.verify_token": "secret-token", "hub.challenge": "12345"},
    )

    assert response.status_code == 200
    assert response.text == "12345"


def test_verify_webhook_rejects_wrong_token(anon_client):
    override_settings(anon_client, meta_verify_token="secret-token")

    response = anon_client.get(
        "/api/v1/webhooks/meta",
        params={"hub.mode": "subscribe", "hub.verify_token": "wrong", "hub.challenge": "12345"},
    )

    assert response.status_code == 403


def test_receive_webhook_rejects_invalid_signature(anon_client):
    override_settings(anon_client, meta_app_secret="app-secret", meta_page_access_token="page-token")
    body = json.dumps(LEADGEN_PAYLOAD).encode()

    response = anon_client.post(
        "/api/v1/webhooks/meta",
        content=body,
        headers={"X-Hub-Signature-256": "sha256=deadbeef", "Content-Type": "application/json"},
    )

    assert response.status_code == 403


def test_receive_webhook_creates_contact_and_lead(anon_client, monkeypatch):
    override_settings(anon_client, meta_app_secret="app-secret", meta_page_access_token="page-token")
    body = json.dumps(LEADGEN_PAYLOAD).encode()

    monkeypatch.setattr(
        "app.api.webhooks.fetch_lead_data",
        lambda leadgen_id, access_token, api_version: {
            "id": leadgen_id,
            "field_data": [
                {"name": "full_name", "values": ["Marko Marković"]},
                {"name": "email", "values": ["marko@example.com"]},
                {"name": "phone_number", "values": ["+381601234567"]},
            ],
        },
    )

    response = anon_client.post(
        "/api/v1/webhooks/meta",
        content=body,
        headers={"X-Hub-Signature-256": sign(body, "app-secret"), "Content-Type": "application/json"},
    )

    assert response.status_code == 200
    assert response.json() == {"processed": 1}

    contacts = anon_client.post(
        "/api/v1/auth/signup", json={"name": "T", "email": "t@example.com", "password": "test1234"}
    )
    token = contacts.json()["access_token"]
    anon_client.headers["Authorization"] = f"Bearer {token}"

    listing = anon_client.get("/api/v1/contacts").json()
    assert any(c["email"] == "marko@example.com" and c["source"] == "facebook" for c in listing)

    leads = anon_client.get("/api/v1/leads").json()
    assert any(lead["stage"] == "new_inquiry" for lead in leads)


def test_receive_webhook_detects_instagram_platform(anon_client, monkeypatch):
    override_settings(anon_client, meta_page_access_token="page-token")
    body = json.dumps(LEADGEN_PAYLOAD).encode()

    monkeypatch.setattr(
        "app.api.webhooks.fetch_lead_data",
        lambda leadgen_id, access_token, api_version: {
            "id": leadgen_id,
            "platform": "ig",
            "field_data": [
                {"name": "full_name", "values": ["Jovana Jovanović"]},
                {"name": "email", "values": ["jovana@example.com"]},
            ],
        },
    )

    response = anon_client.post(
        "/api/v1/webhooks/meta", content=body, headers={"Content-Type": "application/json"}
    )
    assert response.json() == {"processed": 1}

    signup = anon_client.post(
        "/api/v1/auth/signup", json={"name": "T", "email": "t2@example.com", "password": "test1234"}
    )
    anon_client.headers["Authorization"] = f"Bearer {signup.json()['access_token']}"

    listing = anon_client.get("/api/v1/contacts").json()
    assert any(c["email"] == "jovana@example.com" and c["source"] == "instagram" for c in listing)


def test_receive_webhook_is_idempotent_for_same_leadgen_id(anon_client, monkeypatch):
    override_settings(anon_client, meta_page_access_token="page-token")
    body = json.dumps(LEADGEN_PAYLOAD).encode()

    calls = []
    monkeypatch.setattr(
        "app.api.webhooks.fetch_lead_data",
        lambda leadgen_id, access_token, api_version: calls.append(leadgen_id)
        or {"id": leadgen_id, "field_data": [{"name": "full_name", "values": ["Ana"]}]},
    )

    first = anon_client.post("/api/v1/webhooks/meta", content=body, headers={"Content-Type": "application/json"})
    second = anon_client.post("/api/v1/webhooks/meta", content=body, headers={"Content-Type": "application/json"})

    assert first.json() == {"processed": 1}
    assert second.json() == {"processed": 0}
    assert len(calls) == 1


def test_receive_webhook_records_failure_without_page_access_token(anon_client, monkeypatch):
    override_settings(anon_client, meta_page_access_token=None)
    body = json.dumps(LEADGEN_PAYLOAD).encode()

    called = []
    monkeypatch.setattr(
        "app.api.webhooks.fetch_lead_data",
        lambda *args, **kwargs: called.append(True),
    )

    response = anon_client.post("/api/v1/webhooks/meta", content=body, headers={"Content-Type": "application/json"})

    assert response.status_code == 200
    assert response.json() == {"processed": 1}
    assert not called
