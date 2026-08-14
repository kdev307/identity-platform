from rest_framework import status

from apps.common.api.exceptions import ISPAPIException


class EmailAlreadyExistsError(ISPAPIException):
    status_code = status.HTTP_409_CONFLICT
    default_code = "EMAIL_ALREADY_EXISTS"
    default_detail = "An account with this email already exists."