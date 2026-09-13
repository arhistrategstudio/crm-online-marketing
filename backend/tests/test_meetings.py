def create_contact(client, **overrides):
    payload = {"name": "Test Kontakt"}
    payload.update(overrides)
    return client.post("/api/v1/contacts", json=payload).json()


def test_create_meeting_for_existing_contact(client):
    contact = create_contact(client, name="Ana Anić")

    response = client.post(
        "/api/v1/meetings",
        json={
            "contact_id": contact["id"],
            "title": "Sastanak sa Anom",
            "start_at": "2026-09-14T10:00:00",
            "end_at": "2026-09-14T11:00:00",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["contact_id"] == contact["id"]
    assert body["contact_name"] == "Ana Anić"
    assert body["title"] == "Sastanak sa Anom"


def test_create_meeting_without_contact(client):
    response = client.post(
        "/api/v1/meetings",
        json={"title": "Interni sastanak", "start_at": "2026-09-14T09:00:00", "end_at": "2026-09-14T09:30:00"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["contact_id"] is None
    assert body["contact_name"] is None


def test_create_meeting_for_missing_contact_returns_404(client):
    response = client.post(
        "/api/v1/meetings",
        json={"contact_id": 999, "title": "X", "start_at": "2026-09-14T09:00:00", "end_at": "2026-09-14T09:30:00"},
    )

    assert response.status_code == 404


def test_create_meeting_with_end_before_start_returns_422(client):
    response = client.post(
        "/api/v1/meetings",
        json={"title": "X", "start_at": "2026-09-14T11:00:00", "end_at": "2026-09-14T10:00:00"},
    )

    assert response.status_code == 422


def test_list_meetings_filters_by_range(client):
    client.post(
        "/api/v1/meetings",
        json={"title": "Rani", "start_at": "2026-09-01T09:00:00", "end_at": "2026-09-01T09:30:00"},
    )
    client.post(
        "/api/v1/meetings",
        json={"title": "Kasni", "start_at": "2026-09-20T09:00:00", "end_at": "2026-09-20T09:30:00"},
    )

    response = client.get("/api/v1/meetings", params={"start": "2026-09-10T00:00:00", "end": "2026-09-30T00:00:00"})

    assert response.status_code == 200
    titles = {m["title"] for m in response.json()}
    assert titles == {"Kasni"}


def test_delete_meeting(client):
    meeting = client.post(
        "/api/v1/meetings",
        json={"title": "Za brisanje", "start_at": "2026-09-14T09:00:00", "end_at": "2026-09-14T09:30:00"},
    ).json()

    response = client.delete(f"/api/v1/meetings/{meeting['id']}")
    assert response.status_code == 204

    listing = client.get("/api/v1/meetings")
    assert meeting["id"] not in {m["id"] for m in listing.json()}


def test_delete_missing_meeting_returns_404(client):
    response = client.delete("/api/v1/meetings/999")
    assert response.status_code == 404
