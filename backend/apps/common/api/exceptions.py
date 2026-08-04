from rest_framework.exceptions import APIException


class ISPAPIException(APIException):
    status_code = 400
    default_code = "API_ERROR"
    default_detail = "An API error occurred."

    def __init__(
        self,
        detail=None,
        *,
        code=None,
        status_code=None,
    ):
        if status_code is not None:
            self.status_code = status_code

        if code is not None:
            self.default_code = code

        super().__init__(detail or self.default_detail)