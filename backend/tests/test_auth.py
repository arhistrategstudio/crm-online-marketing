from unittest.mock import patch


def test_signup_returns_token_and_user(anon_client):
    response = anon_client.post(
        "/api/v1/auth/signup",
        json={"name": "Ana Vlasnik", "email": "ana@primer.rs", "password": "lozinka123"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["access_token"]
    assert body["user"]["email"] == "ana@primer.rs"
    assert body["user"]["has_password"] is True


def test_signup_duplicate_email_returns_conflict(anon_client):
    payload = {"name": "Ana", "email": "duplikat@primer.rs", "password": "lozinka123"}
    anon_client.post("/api/v1/auth/signup", json=payload)

    response = anon_client.post("/api/v1/auth/signup", json=payload)

    assert response.status_code == 409


def test_login_with_correct_password_succeeds(anon_client):
    anon_client.post(
        "/api/v1/auth/signup",
        json={"name": "Marko", "email": "marko@primer.rs", "password": "tacnalozinka"},
    )

    response = anon_client.post("/api/v1/auth/login", json={"email": "marko@primer.rs", "password": "tacnalozinka"})

    assert response.status_code == 200
    assert response.json()["access_token"]


def test_login_with_wrong_password_returns_unauthorized(anon_client):
    anon_client.post(
        "/api/v1/auth/signup",
        json={"name": "Marko", "email": "marko2@primer.rs", "password": "tacnalozinka"},
    )

    response = anon_client.post("/api/v1/auth/login", json={"email": "marko2@primer.rs", "password": "pogresna"})

    assert response.status_code == 401


def test_login_with_unknown_email_returns_unauthorized(anon_client):
    response = anon_client.post("/api/v1/auth/login", json={"email": "nepostojeci@primer.rs", "password": "bilokoja"})

    assert response.status_code == 401


def test_protected_route_without_token_returns_unauthorized(anon_client):
    response = anon_client.get("/api/v1/contacts")

    assert response.status_code == 401


def test_protected_route_with_token_succeeds(client):
    response = client.get("/api/v1/contacts")

    assert response.status_code == 200


def test_me_returns_current_user(client):
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"


def test_change_password_requires_current_password(client):
    response = client.put(
        "/api/v1/auth/change-password",
        json={"new_password": "novalozinka1"},
    )

    assert response.status_code == 400


def test_change_password_with_correct_current_password_succeeds(client):
    response = client.put(
        "/api/v1/auth/change-password",
        json={"current_password": "test1234", "new_password": "novalozinka1"},
    )

    assert response.status_code == 200

    login = client.post("/api/v1/auth/login", json={"email": "test@example.com", "password": "novalozinka1"})
    assert login.status_code == 200


def test_change_password_without_existing_password_does_not_require_current(anon_client):
    with patch("app.api.auth.google_id_token.verify_oauth2_token") as verify:
        verify.return_value = {"sub": "google-123", "email": "google@primer.rs", "name": "Google Korisnik"}
        with patch("app.api.auth.get_settings") as get_settings:
            get_settings.return_value.google_client_id = "test-client-id"
            google_response = anon_client.post("/api/v1/auth/google", json={"id_token": "fake-token"})
    token = google_response.json()["access_token"]
    anon_client.headers["Authorization"] = f"Bearer {token}"

    response = anon_client.put("/api/v1/auth/change-password", json={"new_password": "prvalozinka1"})

    assert response.status_code == 200
    assert response.json()["has_password"] is True


def test_google_login_creates_new_user(anon_client):
    with patch("app.api.auth.google_id_token.verify_oauth2_token") as verify:
        verify.return_value = {"sub": "google-456", "email": "novi@primer.rs", "name": "Novi Korisnik"}
        with patch("app.api.auth.get_settings") as get_settings:
            get_settings.return_value.google_client_id = "test-client-id"
            response = anon_client.post("/api/v1/auth/google", json={"id_token": "fake-token"})

    assert response.status_code == 200
    body = response.json()
    assert body["user"]["email"] == "novi@primer.rs"
    assert body["user"]["auth_provider"] == "google"
    assert body["user"]["has_password"] is False


def test_google_login_without_configured_client_id_returns_service_unavailable(anon_client):
    with patch("app.api.auth.get_settings") as get_settings:
        get_settings.return_value.google_client_id = None
        response = anon_client.post("/api/v1/auth/google", json={"id_token": "fake-token"})

    assert response.status_code == 503
