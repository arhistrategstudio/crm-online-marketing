import hashlib
import hmac
import json

from app.config import Settings, get_settings
from app.main import app


def override_settings(**overrides):
    base = Settings(_env_file=None)
    for key, value in overrides.items():
        setattr(base, key, value)
    app.dependency_overrides[get_settings] = lambda: base
    return base


def sign(body: bytes, token: str) -> str:
    return hmac.new(token.encode(), body, hashlib.sha256).hexdigest()


MESSAGE_PAYLOAD = {
    "event": "message",
    "timestamp": 1700000000,
    "sender": {"id": "viber-user-1", "name": "Marko Marković"},
    "message": {"type": "text", "text": "Zdravo, zanima me ponuda."},
}


def test_webhook_rejects_invalid_signature(anon_client):
    override_settings(viber_auth_token="viber-secret")
    body = json.dumps(MESSAGE_PAYLOAD).encode()

    response = anon_client.post(
        "/api/v1/webhooks/viber",
        content=body,
        headers={"X-Viber-Content-Signature": "deadbeef", "Content-Type": "application/json"},
    )

    assert response.status_code == 403


def test_webhook_accepts_non_message_events_without_side_effects(anon_client):
    override_settings(viber_auth_token=None)
    body = json.dumps({"event": "webhook", "timestamp": 1700000000}).encode()

    response = anon_client.post("/api/v1/webhooks/viber", content=body, headers={"Content-Type": "application/json"})

    assert response.status_code == 200
    assert response.json() == {"status": 0}


def test_incoming_message_creates_contact_conversation_and_message(anon_client):
    override_settings(viber_auth_token=None)
    body = json.dumps(MESSAGE_PAYLOAD).encode()

    response = anon_client.post("/api/v1/webhooks/viber", content=body, headers={"Content-Type": "application/json"})
    assert response.status_code == 200

    signup = anon_client.post(
        "/api/v1/auth/signup", json={"name": "T", "email": "viber-test@example.com", "password": "test1234"}
    )
    anon_client.headers["Authorization"] = f"Bearer {signup.json()['access_token']}"

    contacts = anon_client.get("/api/v1/contacts").json()
    contact = next(c for c in contacts if c["external_id"] == "viber-user-1")
    assert contact["source"] == "viber"
    assert contact["name"] == "Marko Marković"

    conversations = anon_client.get("/api/v1/conversations").json()
    conversation = next(c for c in conversations if c["contact_id"] == contact["id"])
    assert conversation["channel"] == "viber"

    messages = anon_client.get(f"/api/v1/conversations/{conversation['id']}/messages").json()
    assert any(m["sender"] == "contact" and m["content"] == "Zdravo, zanima me ponuda." for m in messages)


def test_second_message_from_same_sender_reuses_conversation(anon_client):
    override_settings(viber_auth_token=None)
    body = json.dumps(MESSAGE_PAYLOAD).encode()
    anon_client.post("/api/v1/webhooks/viber", content=body, headers={"Content-Type": "application/json"})
    anon_client.post("/api/v1/webhooks/viber", content=body, headers={"Content-Type": "application/json"})

    signup = anon_client.post(
        "/api/v1/auth/signup", json={"name": "T", "email": "viber-test2@example.com", "password": "test1234"}
    )
    anon_client.headers["Authorization"] = f"Bearer {signup.json()['access_token']}"

    contacts = [c for c in anon_client.get("/api/v1/contacts").json() if c["external_id"] == "viber-user-1"]
    assert len(contacts) == 1

    conversations = [c for c in anon_client.get("/api/v1/conversations").json() if c["contact_id"] == contacts[0]["id"]]
    assert len(conversations) == 1


def test_reply_does_not_call_viber_api_when_not_configured(client, monkeypatch):
    override_settings(viber_auth_token=None)
    called = []
    monkeypatch.setattr("app.api.conversations.send_viber_message", lambda *a, **k: called.append(True))

    body = json.dumps(MESSAGE_PAYLOAD).encode()
    client.post("/api/v1/webhooks/viber", content=body, headers={"Content-Type": "application/json"})
    conversation_id = client.get("/api/v1/conversations").json()[0]["id"]

    response = client.post(f"/api/v1/conversations/{conversation_id}/messages", json={"content": "Odgovor"})

    assert response.status_code == 201
    assert response.json()["status"] == "sent"
    assert not called


def test_reply_calls_viber_api_when_configured(client, monkeypatch):
    override_settings(viber_auth_token="viber-secret")
    called = []
    monkeypatch.setattr(
        "app.api.conversations.send_viber_message",
        lambda receiver_id, text, token: called.append((receiver_id, text)),
    )

    body = json.dumps(MESSAGE_PAYLOAD).encode()
    client.post(
        "/api/v1/webhooks/viber",
        content=body,
        headers={"X-Viber-Content-Signature": sign(body, "viber-secret"), "Content-Type": "application/json"},
    )
    conversation_id = client.get("/api/v1/conversations").json()[0]["id"]

    response = client.post(f"/api/v1/conversations/{conversation_id}/messages", json={"content": "Odgovor"})

    assert response.status_code == 201
    assert response.json()["status"] == "sent"
    assert called == [("viber-user-1", "Odgovor")]
