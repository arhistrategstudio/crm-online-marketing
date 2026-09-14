def test_version_endpoint_reports_1_0_0(anon_client):
    response = anon_client.get("/api/v1/version")

    assert response.status_code == 200
    assert response.json()["version"] == "1.0.0"


def test_first_user_becomes_owner_second_user_regular(anon_client):
    first = anon_client.post(
        "/api/v1/auth/signup",
        json={"name": "Prva Vlasnica", "email": "prva@primer.rs", "password": "lozinka123"},
    )
    second = anon_client.post(
        "/api/v1/auth/signup",
        json={"name": "Drugi Korisnik", "email": "drugi@primer.rs", "password": "lozinka123"},
    )

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["user"]["role"] == "Vlasnik"
    assert second.json()["user"]["role"] == "Korisnik"


def test_setup_requires_auth(anon_client):
    response = anon_client.get("/api/v1/dashboard/setup")

    assert response.status_code == 401


def test_setup_status_returns_account_step_done(client):
    response = client.get("/api/v1/dashboard/setup")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["configured"], bool)
    steps = {step["key"]: step for step in body["steps"]}
    assert set(steps) == {"account", "google", "channels", "contacts", "campaigns", "leads"}
    assert steps["account"]["done"] is True