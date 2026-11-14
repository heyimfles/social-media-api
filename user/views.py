from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import generics, status, viewsets, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import serializers

import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.db.models import Count
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from user.serializers import (
    UserSerializer,
    LogoutSerializer,
    UserListSerializer,
    UserDetailSerializer,
    UserRegisterSerializer,
)

from social.models import Follow, Post, Like
from social.serializers import PostListSerializer


class CreateUserView(generics.CreateAPIView):
    """Registers a user"""

    serializer_class = UserRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Returns user's self page, possibility to modify it"""

    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class ManageFollowersView(generics.ListAPIView):
    """Returns self's followers list"""

    serializer_class = UserListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return get_user_model().objects.filter(following__following=self.request.user).annotate(
            comments_count=Count("comments", distinct=True),
            likes_count=Count("likes", distinct=True),
        )


class ManageFollowingView(generics.ListAPIView):
    """Returns self's following list"""

    serializer_class = UserListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return get_user_model().objects.filter(followers__follower=self.request.user).annotate(
            comments_count=Count("comments", distinct=True),
            likes_count=Count("likes", distinct=True),
        )


class ManagePostsView(generics.ListAPIView):
    """Returns self's posts list"""

    serializer_class = PostListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user).annotate(
            comments_count=Count("comments", distinct=True),
            likes_count=Count("likes", distinct=True),
        ).select_related()


class ManageFollowingPostsView(generics.ListAPIView):
    """Returns self following's posts list"""

    serializer_class = PostListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        following_ids = Follow.objects.filter(follower=self.request.user).values(
            "following_id"
        )

        return Post.objects.filter(author_id__in=following_ids, is_published=True).annotate(
            comments_count=Count("comments", distinct=True),
            likes_count=Count("likes", distinct=True),
        ).select_related()


class ManageLikedPostsView(generics.ListAPIView):
    """Returns self's liked posts list"""
    serializer_class = PostListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        liked_ids = Like.objects.filter(author=self.request.user).values()

        return Post.objects.filter(id__in=liked_ids, is_published=True).select_related()


class CustomLogoutView(APIView):
    """Blacklists your refresh token, loging you out"""

    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    @extend_schema(request=LogoutSerializer, responses={200: None})
    def post(self, request) -> Response:
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            token = RefreshToken(serializer.validated_data["refresh_token"])
            if str(token.get("user_id")) != str(request.user.pk):
                return Response(
                    {"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
                )
            token.blacklist()
        except TokenError:
            return Response(
                {"detail": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"detail": "Successfully logged out"}, status=status.HTTP_200_OK
        )


class UserFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(
        lookup_expr="icontains",
    )

    class Meta:
        model = get_user_model()
        fields = ("username",)


class UserViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
):
    """User ViewSet. List, retrieval, filtering by username, follow and unfollow users"""

    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = UserFilter

    def get_serializer_class(self):
        if self.action == "list":
            return UserListSerializer

        if self.action == "retrieve":
            return UserDetailSerializer

        if self.action == "follow":
            return serializers.Serializer

        return UserSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ["list", "retrieve"]:
            queryset = queryset.annotate(
                followers_count=Count("followers", distinct=True),
                following_count=Count("following", distinct=True),
            )
        return queryset

    @action(detail=True, methods=["post", "delete"], url_path="follow")
    def follow(self, request, pk=None):
        target = self.get_object()

        if request.method == "POST":
            if target == request.user:
                return Response(
                    {"detail": "You cannot follow yourself"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            _, created = Follow.objects.get_or_create(
                follower=request.user, following=target
            )
            if not created:
                return Response(
                    {"detail": "You already follow this user"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(status=status.HTTP_201_CREATED)

        deleted, _ = Follow.objects.filter(
            follower=request.user, following=target
        ).delete()

        if not deleted:
            return Response(
                {"detail": "You are not following this user"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)
