from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from user.views import (
    CreateUserView,
    ManageUserView,
    CustomLogoutView,
    UserViewSet,
)

app_name = "user"

router = routers.DefaultRouter()
router.register("users", UserViewSet)

urlpatterns = [
    path(
        "register/",
        CreateUserView.as_view(),
        name="register"
    ),
    path(
        "login/",
        TokenObtainPairView.as_view(),
        name="login"
    ),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh"
    ),
    path(
        "me/",
        ManageUserView.as_view(),
        name="manage"
    ),
    path(
        "logout/",
        CustomLogoutView.as_view(),
        name="logout"
    ),
    path(
        "",
        include(router.urls)
    ),
]