import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import SessionLocal


@pytest.fixture(scope="session")
def client():
    """Returns FastAPI TestClient."""
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
def db_session():
    """Provides a transactional database session for tests."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def admin_token(client):
    """Provides authenticated JWT token for the default admin."""
    res = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "admin", "password": "Admin@BidSphere2026!"},
    )
    assert res.status_code == 200, f"Admin login failed: {res.text}"
    return res.json()["access_token"]


@pytest.fixture(scope="session")
def seller_token(client):
    """Provides authenticated JWT token for seller 'aravind_tech'."""
    res = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "aravind_tech", "password": "Pass@1234"},
    )
    assert res.status_code == 200, f"Seller login failed: {res.text}"
    return res.json()["access_token"]


@pytest.fixture(scope="session")
def buyer_token(client):
    """Provides authenticated JWT token for buyer 'vikram_b'."""
    res = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "vikram_b", "password": "Pass@1234"},
    )
    assert res.status_code == 200, f"Buyer login failed: {res.text}"
    return res.json()["access_token"]


@pytest.fixture(scope="session")
def buyer2_token(client):
    """Provides authenticated JWT token for second buyer 'sneha_rao'."""
    res = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "sneha_rao", "password": "Pass@1234"},
    )
    assert res.status_code == 200, f"Buyer2 login failed: {res.text}"
    return res.json()["access_token"]
