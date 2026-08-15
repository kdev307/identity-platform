from django.urls import path

from .views import RegisterView, LoginView, MeView, RefreshView


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
]