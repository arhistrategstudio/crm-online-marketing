from datetime import datetime, timedelta

from app.models import Channel, Conversation, Lead, Message, Proposal


def create_contact(client, **overrides):
    payload = {"name": "Test Kontakt"}
    payload.update(overrides)
    return client.post("/api/v1/contacts", json=payload).json()


def create_lead(client, contact_id, **overrides):
    payload = {"contact_id": contact_id}
    payload.update(overrides)
    return client.post("/api/v1/leads", json=payload).json()


def test_lead_read_includes_contact_details_and_owner(client):
    contact = create_contact(
        client, name="Firma D.O.O.", phone="060123456", email="firma@example.com",
        source="referral", owner="Marija",
    )
    create_lead(client, contact["id"], value=42000)

    body = client.get("/api/v1/leads").json()[0]

    assert body["contact_phone"] == "060123456"
    assert body["contact_source"] == "referral"
    assert body["contact_owner"] == "Marija"
    assert body["followup_due"] is False
    assert body["proposals_count"] == 0


def test_create_proposal_sets_stage_offer_sent_and_logs_activity(client):
    contact = create_contact(client, name="Ponuda Kontakt")
    lead = create_lead(client, contact["id"], value=10000)

    response = client.post(
        f"/api/v1/leads/{lead['id']}/proposals",
        json={"title": "SEO paket", "amount": 35000, "currency": "RSD"},
    )

    assert response.status_code == 201
    proposal = response.json()
    assert proposal["sent_at"] is not None
    assert proposal["status"] == "sent"

    refreshed = client.get(f"/api/v1/leads/{lead['id']}").json()
    assert refreshed["stage"] == "offer_sent"
    assert refreshed["proposals_count"] == 1
    assert refreshed["next_activity_at"] is not None

    activities = client.get(f"/api/v1/leads/{lead['id']}/activities").json()
    assert any(activity["type"] == "proposal" for activity in activities)


def test_manual_activity_updates_reminder(client):
    contact = create_contact(client, name="Aktivnost Kontakt")
    lead = create_lead(client, contact["id"])

    response = client.post(
        f"/api/v1/leads/{lead['id']}/activities",
        json={
            "type": "call",
            "description": "Pozvati klijenta",
            "next_activity": "Poslati ponudu",
            "next_activity_at": "2026-09-15T10:00:00",
        },
    )

    assert response.status_code == 201
    refreshed = client.get(f"/api/v1/leads/{lead['id']}").json()
    assert refreshed["next_activity"] == "Poslati ponudu"
    assert refreshed["next_activity_at"].startswith("2026-09-15T10:00")


def test_update_lead_records_lost_reason_and_stage_activity(client):
    contact = create_contact(client, name="Izgubljen Kontakt")
    lead = create_lead(client, contact["id"])

    response = client.put(
        f"/api/v1/leads/{lead['id']}",
        json={"stage": "deal_lost", "lost_reason": "Preskupo"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["stage"] == "deal_lost"
    assert body["lost_reason"] == "Preskupo"
    activities = client.get(f"/api/v1/leads/{lead['id']}/activities").json()
    assert any(activity["type"] == "stage_change" for activity in activities)


def test_followups_detects_stale_sent_proposal(client, session_factory):
    contact = create_contact(client, name="Followup Kontakt")
    lead = create_lead(client, contact["id"])
    client.post(f"/api/v1/leads/{lead['id']}/proposals", json={"title": "Predlog", "amount": 1000})

    db = session_factory()
    stored_lead = db.get(Lead, lead["id"])
    old = datetime.now() - timedelta(days=5)
    stored_lead.updated_at = old
    for proposal in db.query(Proposal).filter(Proposal.lead_id == lead["id"]):
        proposal.sent_at = old
    db.commit()
    db.close()

    response = client.get("/api/v1/leads/followups", params={"days": 3})

    assert response.status_code == 200
    body = response.json()
    assert any(item["id"] == lead["id"] and item["followup_due"] for item in body)


def test_lead_history_combines_messages_activities_and_proposals(client, session_factory):
    contact = create_contact(client, name="Istorija Kontakt")
    lead = create_lead(client, contact["id"])
    db = session_factory()
    conversation = Conversation(contact_id=contact["id"], channel=Channel.manual)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    conversation_id = conversation.id
    db.add(Message(conversation_id=conversation_id, sender="contact", content="Zdravo!"))
    db.commit()
    db.close()
    client.post(f"/api/v1/leads/{lead['id']}/proposals", json={"title": "Ponuda A", "amount": 5000})

    response = client.get(f"/api/v1/leads/{lead['id']}/history")

    assert response.status_code == 200
    kinds = {item["kind"] for item in response.json()}
    assert {"message", "activity", "proposal"} <= kinds


def test_dashboard_summary_includes_funnel_and_conversion(client):
    won_contact = create_contact(client, name="Dobijen Kontakt")
    won_lead = create_lead(client, won_contact["id"], value=20000)
    client.put(f"/api/v1/leads/{won_lead['id']}", json={"stage": "paid"})
    lost_contact = create_contact(client, name="Izgubljen Kontakt")
    lost_lead = create_lead(client, lost_contact["id"], value=5000)
    client.put(f"/api/v1/leads/{lost_lead['id']}", json={"stage": "deal_lost", "lost_reason": "Nema budžeta"})

    body = client.get("/api/v1/dashboard/summary").json()

    assert body["won"] == 1
    assert body["lost"] == 1
    assert body["win_rate"] == 50.0
    assert body["closed_this_month_value"] == 20000
    assert body["lost_reasons"] == [{"reason": "Nema budžeta", "count": 1}]
    assert body["avg_time_to_sale_days"] is not None
