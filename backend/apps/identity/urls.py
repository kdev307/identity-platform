from django.urls import path

from .views import LoginView, RegisterView


urlpatterns = [
    # Register
    path(
        "register/",
        RegisterView.as_view(),
        name="register",
    ),
    # Login
    path(
        "login/",
        LoginView.as_view(),
        name="login",
    ),
]