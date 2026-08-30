import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.identity.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def registration_payload():
    return {
        "email": "test@example.com",
        "password": "StrongPassword123!",
        "password_confirmation": "StrongPassword123!",
        "first_name": "Test",
        "last_name": "User",
    }


@pytest.fixture
def user():
    return User.objects.create_user(
        email="user@example.com",
        password="StrongPassword123!",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def login_payload(user):
    return {
        "email": user.email,
        "password": "StrongPassword123!",
    }


@pytest.fixture
def user_token_pair(user):
    refresh = RefreshToken.for_user(user)

    return {
        "access_token": str(refresh.access_token),
        "refresh_token": str(refresh),
    }


@pytest.fixture
def user_access_token(user_token_pair):
    return user_token_pair["access_token"]

@pytest.fixture
def user_refresh_token(user_token_pair):
    return user_token_pair["refresh_token"]



@pytest.fixture
def authenticated_client(
    api_client,
    user_access_token
):
    api_client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {user_access_token}"
    )

    return api_client