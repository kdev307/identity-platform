import pytest
from django.urls import reverse
from rest_framework import status

LOGOUT_URL = reverse("logout")
REFRESH_URL = reverse("refresh")

# Test Case 01 - Successful Logout
@pytest.mark.django_db
def test_authenticated_user_can_logout(
    authenticated_client,
    user_refresh_token
):
    response = authenticated_client.post(
        LOGOUT_URL,
        {
            "refresh_token": user_refresh_token
        },
        format="json"
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["data"]["message"] == "Logout successful."
    assert response.data["error"] is None
    assert response.data["meta"] == {}


# Test Case 02 - Verifying blacklisted token - Logged-out refresh token cannot be used
@pytest.mark.django_db
def test_logged_out_refresh_token_cannot_be_used(
    authenticated_client,
    api_client,
    user_refresh_token
):
    logout_response = authenticated_client.post(
        LOGOUT_URL,
        {
            "refresh_token": user_refresh_token
        },
        format="json"
    )

    assert logout_response.status_code == status.HTTP_200_OK

    refresh_response = api_client.post(
        REFRESH_URL,
        {
            "refresh_token": user_refresh_token
        },
        format="json"
    )

    assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED

    assert refresh_response.data["data"] is None
    assert (
        refresh_response.data["error"]["code"]
        == "INVALID_REFRESH_TOKEN"
    )
    assert refresh_response.data["meta"] == {}


# Test Case 03 - Unsuccessful logout (Unauthenticated user)
@pytest.mark.django_db
def test_unauthenticated_user_cannot_logout(
    api_client,
    user_refresh_token
):
    response = api_client.post(
        LOGOUT_URL,
        {
            "refresh_token": user_refresh_token
        },
        format="json"
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    assert response.data["data"] is None
    assert (
        response.data["error"]["code"]
        == "not_authenticated"
    )
    assert response.data["meta"] == {}


# Test Case 03 - Unsuccessful logout (logout without refresh_token)
@pytest.mark.django_db
def test_authenticated_user_cannot_logout_without_refresh_token(
    authenticated_client
):
    response = authenticated_client.post(
        LOGOUT_URL,
        {},
        format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert response.data["data"] is None
    assert response.data["error"]["code"] == "VALIDATION_ERROR"
    assert response.data["meta"] == {}


# Test Case 03 - Unsuccessful logout (logout without refresh_token)
@pytest.mark.django_db
def test_authenticated_user_cannot_logout_with_invalid_refresh_token(
    authenticated_client
):
    response = authenticated_client.post(
        LOGOUT_URL,
        {
            "refresh_token": "invalid_token"
        },
        format="json"
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    assert response.data["data"] is None
    assert response.data["error"]["code"] == "INVALID_REFRESH_TOKEN"
    assert response.data["meta"] == {}
