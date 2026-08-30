from rest_framework import status

from apps.common.api.exceptions import ISPAPIException


class EmailAlreadyExistsError(ISPAPIException):
    status_code = status.HTTP_409_CONFLICT
    default_code = "EMAIL_ALREADY_EXISTS"
    default_detail = "An account with this email already exists."

class InvalidCredentialsError(ISPAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_code = "INVALID_CREDENTIALS"
    default_detail = "Invalid email or password."

class InvalidRefreshTokenError(ISPAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_code = "INVALID_REFRESH_TOKEN"
    default_detail = "The refresh token is invalid, expired, or blacklisted."