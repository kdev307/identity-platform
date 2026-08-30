import pytest
from rest_framework import status

REFRESH_URL = "/api/v1/auth/refresh/"

# Test Case 01 - Valid Refresh Token
@pytest.mark.django_db
def test_user_can_refresh_tokens(
    api_client,
    user_token_pair
):
    old_access_token = user_token_pair["access_token"]
    old_refresh_token = user_token_pair["refresh_token"]

    response = api_client.post(
        REFRESH_URL,
        data={
            "refresh_token": old_refresh_token
        },
        format="json"
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.data["data"]

    assert data["access_token"]
    assert data["refresh_token"]
    assert data["token_type"] == "Bearer"

    assert data["access_token"] != old_access_token
    assert data["refresh_token"] != old_refresh_token


# Test Case 02 - Token BlackListing (Invalidating Old Tokens)
@pytest.mark.django_db
def test_rotated_refresh_token_cannot_be_reused(
    api_client,
    user_refresh_token
):
    first_response = api_client.post(
        REFRESH_URL,
        {
            "refresh_token": user_refresh_token
        },
        format="json"
    )

    assert first_response.status_code == status.HTTP_200_OK

    second_response = api_client.post(
        REFRESH_URL,
        {
            "refresh_token": user_refresh_token,
        },
        format="json",
    )

    assert second_response.status_code == status.HTTP_401_UNAUTHORIZED


# Test Case 03 - Invalid Refresh Token
@pytest.mark.django_db
def test_user_cannot_refresh_with_invalid_token(
    api_client
):
    response = api_client.post(
        REFRESH_URL,
        {
            "refresh_token": "invalid.token.here"
        },
        format="json"
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    assert response.data["data"] is None
    assert response.data["error"]["code"] == "INVALID_REFRESH_TOKEN"
    assert response.data["meta"] == {}


# Test Case 04 - Invalid Refresh Token
@pytest.mark.django_db
def test_user_cannot_refresh_without_token(
    api_client,
):
    response = api_client.post(
        REFRESH_URL,
        {},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert response.data["data"] is None
    assert response.data["error"]["code"] == "VALIDATION_ERROR"
    assert response.data["meta"] == {}