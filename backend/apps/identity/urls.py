from django.urls import path

from .views import RegisterView, LoginView, MeView


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
    # Me
    path(
        "me/",
        MeView.as_view(),
        name="me",
    ),
]