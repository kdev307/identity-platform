import pytest
from rest_framework import status

ME_URL = '/api/v1/auth/me/'

# Test Case 01 - Successful profile access
@pytest.mark.django_db
def test_authenticated_user_can_access_me(
    authenticated_client, 
    user
):
    response = authenticated_client.get(ME_URL)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["error"] is None

    data = response.data["data"]

    assert data["id"] == str(user.id)
    assert data["email"] == user.email
    assert data["first_name"] == user.first_name
    assert data["last_name"] == user.last_name

# Test Case 02 - Unsuccessful profile access - unauthenticated user
@pytest.mark.django_db
def test_unauthenticated_user_cannot_access_me(
    api_client,
):
    response = api_client.get(ME_URL)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data["data"] is None
    assert response.data["error"]["code"] == "not_authenticated"
    assert response.data["meta"] == {}


# Test Case 03 - Unsuccessful profile access - invalid access token
@pytest.mark.django_db
def test_user_cannot_access_me_with_invalid_token(
    api_client,
):
    api_client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')
    response = api_client.get(ME_URL)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data["data"] is None
    assert response.data["error"]["code"] == "token_not_valid"
    assert response.data["meta"] == {}