from rest_framework.views import exception_handler


def isp_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return response

    detail = response.data

    if isinstance(detail, dict):
        message = detail.get("detail")

        if message:
            error = {
                "code": getattr(
                    exc,
                    "default_code",
                    "API_ERROR",
                ),
                "message": str(message),
            }
        else:
            error = {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed.",
                "details": detail,
            }

    else:
        error = {
            "code": "API_ERROR",
            "message": str(detail),
        }

    response.data = {
        "data": None,
        "error": error,
        "meta": {},
    }

    return response