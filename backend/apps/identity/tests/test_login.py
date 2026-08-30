import pytest
from rest_framework import status

LOGIN_URL = "/api/v1/auth/login/"


# Test Case 01 - Successful user login
@pytest.mark.django_db
def test_user_can_login(
    api_client,
    login_payload,
    user,
):

    response = api_client.post(
        LOGIN_URL,
        login_payload,
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["error"] is None

    data = response.data["data"]

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "Bearer"

    assert data["user"]["id"] == str(user.id)
    assert data["user"]["email"] == user.email


# Test Case 02 - Unsuccessful user login -- invalid password
@pytest.mark.django_db
def test_user_cannot_login_with_incorrect_password(
    api_client,
    login_payload,
):
    login_payload["password"] = "WrongPassword123!"

    response = api_client.post(
        LOGIN_URL,
        login_payload,
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    assert response.data["data"] is None
    assert response.data["error"]["code"] == "INVALID_CREDENTIALS"
    assert response.data["error"]["message"] == (
        "Invalid email or password."
    )

# Test Case 03 - Unsuccessful user login -- non-existent user
@pytest.mark.django_db
def test_nonexistent_user_cannot_login(
    api_client,
    login_payload,
):
    login_payload["email"] = "unknown@example.com"

    response = api_client.post(
        LOGIN_URL,
        login_payload,
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    assert response.data["data"] is None
    assert response.data["error"]["code"] == "INVALID_CREDENTIALS"
    assert response.data["error"]["message"] == (
        "Invalid email or password."
    )


# Test Case 04 - Unsuccessful user login -- inactive user
@pytest.mark.django_db
def test_inactive_user_cannot_login(
    api_client,
    user,
    login_payload,
):
    user.is_active = False
    user.save()

    response = api_client.post(
        LOGIN_URL,
        login_payload,
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    assert response.data["data"] is None
    assert response.data["error"]["code"] == "INVALID_CREDENTIALS"
    assert response.data["error"]["message"] == (
        "Invalid email or password."
    )