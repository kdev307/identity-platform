from rest_framework.views import exception_handler

from apps.common.api.exceptions import ISPAPIException


def isp_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return response

    detail = response.data

    if isinstance(exc, ISPAPIException):
        error = {
            "code": exc.default_code,
            "message": str(exc.detail),
            "details": None,
        }
    elif isinstance(detail, dict) and "detail" in detail:
        error = {
            "code": getattr(
                exc,
                "default_code",
                "API_ERROR",
            ),
            "message": str(detail["detail"]),
            "details": None,
        }

    elif isinstance(detail, dict):
        error = {
            "code": "VALIDATION_ERROR",
            "message": "Request validation failed.",
            "details": detail,
        }

    else:
        error = {
            "code": getattr(
                exc,
                "default_code",
                "API_ERROR",
            ),
            "message": str(detail),
            "details": None,
        }

    response.data = {
        "data": None,
        "error": error,
        "meta": {},
    }

    return response