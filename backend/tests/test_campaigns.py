def create_campaign(client, **overrides):
    payload = {"name": "Test kampanja", "channel": "instagram", "status": "active", "budget": 10000, "spend": 4000}
    payload.update(overrides)
    return client.post("/api/v1/campaigns", json=payload)


def test_create_campaign_returns_created_campaign(client):
    response = create_campaign(client)

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Test kampanja"
    assert body["leads_count"] == 0
    assert body["cost_per_lead"] is None
    assert body["conversion_rate"] is None


def test_list_campaigns_returns_created_campaigns(client):
    create_campaign(client, name="Kampanja A")
    create_campaign(client, name="Kampanja B")

    response = client.get("/api/v1/campaigns")

    assert response.status_code == 200
    names = {item["name"] for item in response.json()}
    assert names == {"Kampanja A", "Kampanja B"}


def test_campaign_kpis_reflect_attributed_leads(client):
    campaign = create_campaign(client, spend=6000).json()
    contact = client.post("/api/v1/contacts", json={"name": "Lead Kontakt"}).json()
    client.post(
        "/api/v1/leads",
        json={"contact_id": contact["id"], "campaign_id": campaign["id"], "stage": "scheduled_paid"},
    )

    response = client.get(f"/api/v1/campaigns/{campaign['id']}")

    assert response.status_code == 200
    body = response.json()
    assert body["leads_count"] == 1
    assert body["cost_per_lead"] == 6000
    assert body["conversion_rate"] == 100.0


def test_update_campaign_changes_fields(client):
    campaign = create_campaign(client).json()

    response = client.put(
        f"/api/v1/campaigns/{campaign['id']}",
        json={"name": "Test kampanja", "channel": "instagram", "status": "paused", "budget": 10000, "spend": 8000},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "paused"
    assert response.json()["spend"] == 8000


def test_get_unknown_campaign_returns_not_found(client):
    response = client.get("/api/v1/campaigns/999")

    assert response.status_code == 404


def test_delete_campaign_removes_it(client):
    campaign = create_campaign(client).json()

    response = client.delete(f"/api/v1/campaigns/{campaign['id']}")
    assert response.status_code == 204

    response = client.get(f"/api/v1/campaigns/{campaign['id']}")
    assert response.status_code == 404


def test_dashboard_summary_includes_campaign_kpis(client):
    campaign = create_campaign(client, status="active", spend=5000).json()
    contact = client.post("/api/v1/contacts", json={"name": "Dashboard Kontakt"}).json()
    client.post("/api/v1/leads", json={"contact_id": contact["id"], "campaign_id": campaign["id"]})

    response = client.get("/api/v1/dashboard/summary")

    assert response.status_code == 200
    body = response.json()
    assert body["campaigns_active"] == 1
    assert body["avg_cost_per_lead"] == 5000
