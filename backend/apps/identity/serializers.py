from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    InvalidRefreshTokenError
)

from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[],
    )
     
    password = serializers.CharField(
        write_only=True,
        required=True,
        trim_whitespace=False,
    )

    password_confirmation = serializers.CharField(
        write_only=True,
        required=True,
        trim_whitespace=False,
    )

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "password_confirmation",
            "first_name",
            "last_name",
        )

    def validate_email(self, value):
        email = value.strip().lower()

        if User.objects.filter(email=email).exists():
            raise EmailAlreadyExistsError()

        return email

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirmation"]:
            raise serializers.ValidationError(
                {
                    "password_confirmation": "Passwords do not match.",
                }
            )

        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirmation")

        return User.objects.create_user(
            **validated_data,
        )

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
    )

    password = serializers.CharField(
        write_only=True,
        required=True,
        trim_whitespace=False,
    )

    def validate(self, attrs):
        email = attrs["email"].strip().lower()
        password = attrs["password"]

        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password,
        )

        if user is None or not user.is_active:
            raise InvalidCredentialsError()

        attrs["user"] = user

        return attrs


class RefreshSerializer(serializers.Serializer):
    """
    Refresh token serializer for the ISP API.

    Exposes `refresh_token` as the public API contract while
    delegating token validation and rotation to Simple JWT.
    """

    refresh_token = serializers.CharField(
        write_only=True,
        required=True,
        trim_whitespace=False,
    )

    def validate(self, attrs):
        serializer = TokenRefreshSerializer(
            data={
                "refresh": attrs["refresh_token"],
            }
        )
        try:
            serializer.is_valid(raise_exception=True)

        except TokenError:
                raise InvalidRefreshTokenError()

        return serializer.validated_data

class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(
        write_only=True,
        required=True,
        trim_whitespace=False,
    )

    def validate(self, attrs):
        try:
            refresh = RefreshToken(attrs["refresh_token"])
            attrs["refresh"] = refresh

        except TokenError:
             raise InvalidRefreshTokenError()

        return attrs


    def save(self, **kwargs):
        refresh = self.validated_data["refresh"]

        try:
            refresh.blacklist()
        except AttributeError:
            raise serializers.ValidationError(
                {
                    "refresh_token": "Token blacklisting is not available.",
                }
            )

        return None