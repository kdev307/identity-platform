from django.urls import path

from .views import (
    LoginView,
    LogoutView,
    MeView,
    RefreshView,
    RegisterView,
)

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

    # Refresh Token
    path(
        "refresh/",
        RefreshView.as_view(),
        name="refresh",
    ),

    # Logout
    path(
        "logout/",
        LogoutView.as_view(),
        name="logout",
    ),
]