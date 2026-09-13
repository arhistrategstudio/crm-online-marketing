def create_contact(client, **overrides):
    payload = {"name": "Test Kontakt"}
    payload.update(overrides)
    return client.post("/api/v1/contacts", json=payload).json()


def test_create_lead_for_existing_contact(client):
    contact = create_contact(client, name="Ana Anić")

    response = client.post("/api/v1/leads", json={"contact_id": contact["id"], "value": 1000})

    assert response.status_code == 201
    body = response.json()
    assert body["contact_id"] == contact["id"]
    assert body["stage"] == "new_inquiry"
    assert body["value"] == 1000


def test_create_lead_for_missing_contact_returns_404(client):
    response = client.post("/api/v1/leads", json={"contact_id": 999})

    assert response.status_code == 404


def test_create_duplicate_lead_for_same_contact_returns_409(client):
    contact = create_contact(client, name="Petar Petrić")
    client.post("/api/v1/leads", json={"contact_id": contact["id"]})

    response = client.post("/api/v1/leads", json={"contact_id": contact["id"]})

    assert response.status_code == 409


def test_list_leads_returns_created_leads(client):
    first_contact = create_contact(client, name="Prvi Kontakt")
    second_contact = create_contact(client, name="Drugi Kontakt")
    client.post("/api/v1/leads", json={"contact_id": first_contact["id"]})
    client.post("/api/v1/leads", json={"contact_id": second_contact["id"]})

    response = client.get("/api/v1/leads")

    assert response.status_code == 200
    contact_ids = {lead["contact_id"] for lead in response.json()}
    assert contact_ids == {first_contact["id"], second_contact["id"]}


def test_update_lead_changes_stage_and_value(client):
    contact = create_contact(client, name="Lead Kontakt")
    lead = client.post("/api/v1/leads", json={"contact_id": contact["id"]}).json()

    response = client.put(
        f"/api/v1/leads/{lead['id']}",
        json={"stage": "offer_sent", "value": 5000},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["stage"] == "offer_sent"
    assert body["value"] == 5000


def test_update_lead_without_value_keeps_existing_value(client):
    contact = create_contact(client, name="Lead Kontakt Dva")
    lead = client.post(
        "/api/v1/leads", json={"contact_id": contact["id"], "value": 2500}
    ).json()

    response = client.put(f"/api/v1/leads/{lead['id']}", json={"stage": "waiting_response"})

    assert response.status_code == 200
    body = response.json()
    assert body["stage"] == "waiting_response"
    assert body["value"] == 2500


def test_update_lead_returns_404_when_missing(client):
    response = client.put("/api/v1/leads/999", json={"stage": "offer_sent"})

    assert response.status_code == 404
