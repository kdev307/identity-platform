from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .exceptions import EmailAlreadyExistsError

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

        if user is None:
            raise serializers.ValidationError(
                {
                    "credentials": "Invalid email or password.",
                }
            )

        if not user.is_active:
            raise serializers.ValidationError(
                {
                    "credentials": "User account is inactive.",
                }
            )

        attrs["user"] = user

        return attrs


class RefreshSerializer(TokenRefreshSerializer):
    """
    Custom refresh serializer.

    Delegates JWT validation and refresh-token rotation
    to Simple JWT while allowing the ISP API layer to
    control how the endpoint is exposed.
    """

    pass

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
            raise serializers.ValidationError(
                {
                    "refresh_token": "Invalid or expired refresh token.",
                }
            )

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