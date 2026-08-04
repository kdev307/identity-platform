from django.urls import path

from .views import HealthCheckView, ReadinessCheckView


urlpatterns = [    
    path("", HealthCheckView.as_view(), name="health"),
    path("ready/", ReadinessCheckView.as_view(), name="readiness"),

]