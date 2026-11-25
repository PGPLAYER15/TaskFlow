import pytest


@pytest.fixture
def registered_user(client, fake):
    password = fake.password(length=12)
    payload = {
        "email": fake.email(),
        "username": fake.user_name(),
        "password": password,
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    return {"payload": payload, "password": password, "data": response.json()}


# 1. Happy Paths
def test_register_success(client, fake):
    payload = {
        "email": fake.email(),
        "username": fake.user_name(),
        "password": fake.password(length=12),
    }
    response = client.post("/api/auth/register", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["username"] == payload["username"]


def test_login_success(client, registered_user):
    response = client.post(
        "/api/auth/login",
        data={
            "username": registered_user["payload"]["email"],
            "password": registered_user["password"],
        },
    )

    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"


# 2. Failure Paths
def test_login_fails_with_wrong_password(client, registered_user, fake):
    response = client.post(
        "/api/auth/login",
        data={
            "username": registered_user["payload"]["email"],
            "password": fake.password(length=16),
        },
    )
    assert response.status_code == 401


def test_register_fails_with_duplicate_email(client, registered_user, fake):
    duplicate_payload = {
        "email": registered_user["payload"]["email"],
        "username": fake.user_name(),
        "password": fake.password(length=12),
    }
    response = client.post("/api/auth/register", json=duplicate_payload)
    
    assert response.status_code == 400
