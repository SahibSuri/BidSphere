import uuid
import pytest


def test_registration_and_login_success(client):
    """Test user registration followed by successful authentication."""
    unique_suffix = uuid.uuid4().hex[:6]
    username = f"testbuyer_{unique_suffix}"
    email = f"testbuyer_{unique_suffix}@example.com"
    password = "TestPassword@2026"

    # Register
    reg_res = client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
            "full_name": "Automated Test Buyer",
            "role": "BUYER",
            "phone": "+91-9988776655",
            "address": "Bangalore Test Lab",
        },
    )
    assert reg_res.status_code == 201
    reg_data = reg_res.json()
    assert reg_data["username"] == username
    assert reg_data["email"] == email
    assert "password_hash" not in reg_data

    # Login
    login_res = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": username, "password": password},
    )
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    assert token_data["username"] == username


def test_duplicate_email_rejection(client):
    """Test registration rejects existing registered email."""
    res = client.post(
        "/api/v1/auth/register",
        json={
            "username": f"user_{uuid.uuid4().hex[:6]}",
            "email": "admin@bidsphere.com",  # Already registered admin
            "password": "Password@123",
            "full_name": "Duplicate Tester",
            "role": "BUYER",
        },
    )
    assert res.status_code == 409
    assert "already registered" in res.json()["detail"].lower()


def test_duplicate_username_rejection(client):
    """Test registration rejects existing registered username."""
    res = client.post(
        "/api/v1/auth/register",
        json={
            "username": "admin",  # Already taken
            "email": f"unique_{uuid.uuid4().hex[:6]}@example.com",
            "password": "Password@123",
            "full_name": "Duplicate Tester",
            "role": "BUYER",
        },
    )
    assert res.status_code == 409
    assert "already taken" in res.json()["detail"].lower()


def test_invalid_password_rejection(client):
    """Test login with bad credentials returns 401."""
    res = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "admin", "password": "WrongPassword@999"},
    )
    assert res.status_code == 401
    assert "Invalid credentials" in res.json()["detail"]


def test_inactive_account_rejection(client):
    """Test inactive account is blocked from logging in."""
    res = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "inactive_user", "password": "Pass@1234"},
    )
    assert res.status_code == 403
    assert "deactivated" in res.json()["detail"].lower()


def test_role_based_access_control(client, buyer_token, admin_token):
    """Test that a regular buyer cannot access administrative endpoints."""
    # Buyer attempts to access admin dashboard -> 403 Forbidden
    buyer_headers = {"Authorization": f"Bearer {buyer_token}"}
    res_buyer = client.get("/api/v1/admin/dashboard", headers=buyer_headers)
    assert res_buyer.status_code == 403

    # Admin accesses admin dashboard -> 200 OK
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    res_admin = client.get("/api/v1/admin/dashboard", headers=admin_headers)
    assert res_admin.status_code == 200
    assert "kpis" in res_admin.json()
