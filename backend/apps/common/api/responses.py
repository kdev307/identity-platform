from rest_framework.response import Response


def success_response(
    data=None,
    *,
    status=200,
    meta=None,
):
    return Response(
        {
            "data": data,
            "error": None,
            "meta": meta or {},
        },
        status=status,
    )