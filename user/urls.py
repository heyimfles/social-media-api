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
    ManageFollowersView,
    ManageFollowingView,
    ManagePostsView,
    ManageFollowingPostsView
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
        "logout/",
        CustomLogoutView.as_view(),
        name="logout"
    ),
    path(
        "me/",
        ManageUserView.as_view(),
        name="manage"
    ),
    path(
        "me/followers/",
        ManageFollowersView.as_view(),
        name="my_followers"
    ),
    path(
        "me/following/",
        ManageFollowingView.as_view(),
        name="my_following"
    ),
    path(
        "me/posts/",
        ManagePostsView.as_view(),
        name="my_posts"
    ),
    path(
        "me/following/posts/",
        ManageFollowingPostsView.as_view(),
        name="my_following_posts"
    ),
    path(
        "",
        include(router.urls)
    ),
]