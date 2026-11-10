from django.urls import path, include
from rest_framework import routers

from social.views import (
    PostViewSet,
)

router = routers.DefaultRouter()
router.register("posts", PostViewSet)

urlpatterns = [
    path(
        "",
        include(router.urls)
    ),
]

app_name = "social"
