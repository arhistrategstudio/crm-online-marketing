import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_db
from app.main import app
from app.models import Base


@pytest.fixture()
def anon_client():
    """Provides a TestClient backed by an isolated in-memory SQLite database, without auth.

    Uses StaticPool so every session shares the same in-memory connection,
    and skips the app lifespan so the real dev database file is never touched.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def client(anon_client):
    """Same isolated database as anon_client, but pre-authenticated as a signed-up test user."""
    signup = anon_client.post(
        "/api/v1/auth/signup",
        json={"name": "Test korisnik", "email": "test@example.com", "password": "test1234"},
    )
    token = signup.json()["access_token"]
    anon_client.headers["Authorization"] = f"Bearer {token}"
    return anon_client
