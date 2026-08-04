from django.db import connection
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    authentication_classes = []
    permission_classes = [] 

    def get(self, request):
        return Response(
            {
                "status": "ok",
            }
        )


class ReadinessCheckView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        database_status = self._check_database()

        is_ready = database_status == "ok"

        return Response(
            {
                "status": "ok" if is_ready else "unavailable",
                "services": {
                    "database": database_status,
                },
            },
            status=200 if is_ready else 503,
        )

    @staticmethod
    def _check_database():
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")

            return "ok"

        except Exception:
            return "unavailable"
    