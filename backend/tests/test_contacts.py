def test_create_contact_returns_created_contact(client):
    response = client.post(
        "/api/v1/contacts",
        json={"name": "Ana Petrović", "phone": "+381601111111", "email": "ana@example.com"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Ana Petrović"
    assert body["status"] == "Aktivan"
    assert body["source"] == "manual"
    assert body["id"]


def test_create_contact_duplicate_phone_returns_conflict(client):
    payload = {"name": "Marko Marković", "phone": "+381602222222"}
    client.post("/api/v1/contacts", json=payload)

    response = client.post("/api/v1/contacts", json={"name": "Drugo Ime", "phone": "+381602222222"})

    assert response.status_code == 409


def test_create_contact_duplicate_email_returns_conflict(client):
    client.post("/api/v1/contacts", json={"name": "Jovana Jovanović", "email": "jovana@example.com"})

    response = client.post("/api/v1/contacts", json={"name": "Neko Drugi", "email": "jovana@example.com"})

    assert response.status_code == 409


def test_create_contact_duplicate_external_id_returns_conflict(client):
    client.post("/api/v1/contacts", json={"name": "Petar Petrović", "external_id": "fb-123"})

    response = client.post("/api/v1/contacts", json={"name": "Neko Drugi", "external_id": "fb-123"})

    assert response.status_code == 409


def test_list_contacts_filters_by_search_term(client):
    client.post("/api/v1/contacts", json={"name": "Milica Ilić", "email": "milica@example.com"})
    client.post("/api/v1/contacts", json={"name": "Nikola Nikolić", "phone": "+381603333333"})

    response = client.get("/api/v1/contacts", params={"search": "Milica"})

    assert response.status_code == 200
    names = [contact["name"] for contact in response.json()]
    assert names == ["Milica Ilić"]


def test_list_contacts_returns_all_when_no_search(client):
    client.post("/api/v1/contacts", json={"name": "Prvi Kontakt"})
    client.post("/api/v1/contacts", json={"name": "Drugi Kontakt"})

    response = client.get("/api/v1/contacts")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_contact_returns_404_when_missing(client):
    response = client.get("/api/v1/contacts/999")

    assert response.status_code == 404


def test_get_contact_returns_existing_contact(client):
    created = client.post("/api/v1/contacts", json={"name": "Ivana Ivić"}).json()

    response = client.get(f"/api/v1/contacts/{created['id']}")

    assert response.status_code == 200
    assert response.json()["name"] == "Ivana Ivić"


def test_update_contact_changes_fields(client):
    created = client.post("/api/v1/contacts", json={"name": "Stefan Stefanović"}).json()

    response = client.put(
        f"/api/v1/contacts/{created['id']}",
        json={"name": "Stefan S.", "status": "Neaktivan"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Stefan S."
    assert body["status"] == "Neaktivan"


def test_update_contact_returns_404_when_missing(client):
    response = client.put("/api/v1/contacts/999", json={"name": "Nepostojeći"})

    assert response.status_code == 404
