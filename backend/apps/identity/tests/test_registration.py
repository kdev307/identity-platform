import pytest
from rest_framework import status

from apps.identity.models import User

REGISTER_URL = '/api/v1/auth/register/'

# Test Case 01 - Successful user registration
@pytest.mark.django_db
def test_user_can_register(  api_client,
    registration_payload,):

    payload = {
        "email": "test@example.com",
        "password": "Test@1234",
        "password_confirmation": "Test@1234",
        "first_name": "Script Test",
        "last_name": "User"
    }

    response = api_client.post(
        REGISTER_URL, registration_payload, format='json'
    )

    assert response.status_code == status.HTTP_201_CREATED

    assert response.data["data"]["email"] == (
        registration_payload["email"]
    )
    assert response.data["error"] is None

    user = User.objects.get(
        email = registration_payload["email"]
    )

    assert user.first_name == registration_payload["first_name"]
    assert user.last_name == registration_payload["last_name"]

    assert user.check_password(
        registration_payload["password"]
    )

# Test Case 02 - Unsuccessful user registration -- duplicate email
@pytest.mark.django_db
def test_user_cannot_register_with_existing_email( api_client,
    registration_payload,
    user,):

    registration_payload["email"] = user.email

    response = api_client.post(
        REGISTER_URL,
        registration_payload,
        format="json",
    )

    assert response.status_code == status.HTTP_409_CONFLICT

    assert response.data["data"] is None
    assert response.data["error"]["code"] == (
        "EMAIL_ALREADY_EXISTS"
    )

# Test Case 03 - Unsuccessful user registration -- mismatched passwords
@pytest.mark.django_db
def test_user_cannot_register_with_mismatched_passwords(
    api_client,
    registration_payload,
):
    registration_payload["password_confirmation"] = (
        "DifferentPassword123!"
    )

    response = api_client.post(
        REGISTER_URL,
        registration_payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert response.data["data"] is None
    assert response.data["error"]["code"] == "VALIDATION_ERROR"

    assert "password_confirmation" in (
        response.data["error"]["details"]
    )


# Test Case 01 - Unsuccessful user registration -- invalid password
@pytest.mark.django_db
def test_user_cannot_register_with_invalid_password(
    api_client,
    registration_payload,
):
    registration_payload["password"] = "123"
    registration_payload["password_confirmation"] = "123"

    response = api_client.post(
        REGISTER_URL,
        registration_payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert response.data["data"] is None
    assert response.data["error"]["code"] == "VALIDATION_ERROR"

    assert "password" in response.data["error"]["details"]
