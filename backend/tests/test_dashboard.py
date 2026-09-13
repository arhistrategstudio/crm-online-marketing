def create_contact(client, **overrides):
    payload = {"name": "Test Kontakt"}
    payload.update(overrides)
    return client.post("/api/v1/contacts", json=payload).json()


def test_prospects_returns_leads_with_contact_name(client):
    contact = create_contact(client, name="Nikola Nikolić")
    client.post("/api/v1/leads", json={"contact_id": contact["id"], "value": 3000})

    response = client.get("/api/v1/dashboard/prospects")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["name"] == "Nikola Nikolić"
    assert body[0]["stage"] == "new_inquiry"
    assert body[0]["value"] == 3000


def test_prospects_respects_limit(client):
    for i in range(3):
        contact = create_contact(client, name=f"Kontakt {i}")
        client.post("/api/v1/leads", json={"contact_id": contact["id"]})

    response = client.get("/api/v1/dashboard/prospects", params={"limit": 2})

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_notifications_include_new_inquiry_leads(client):
    contact = create_contact(client, name="Jovana Jovanović")
    client.post("/api/v1/leads", json={"contact_id": contact["id"]})

    response = client.get("/api/v1/dashboard/notifications")

    assert response.status_code == 200
    body = response.json()
    assert body["count"] >= 1
    assert any(item["type"] == "lead" and "Jovana Jovanović" in item["text"] for item in body["items"])
