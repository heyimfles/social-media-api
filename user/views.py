from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status, viewsets, mixins
from rest_framework.response import Response
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework.decorators import action
from rest_framework import serializers

import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.db.models import Count

from user.serializers import (
    UserSerializer,
    LogoutSerializer,
    UserListSerializer,
    UserDetailSerializer,
    UserRegisterSerializer
)

from social.models import (
    Follow
)


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class CustomLogoutView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    @extend_schema(
        request=LogoutSerializer,
        responses={200: None}
    )
    def post(self, request):
        for token in OutstandingToken.objects.filter(user=request.user):
            BlacklistedToken.objects.get_or_create(token=token)
        return Response(
            {"detail": "Successfully logged out."},
            status=status.HTTP_200_OK,
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
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
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

    @action(
        detail=True,
        methods=["post", "delete"],
        url_path="follow"
    )
    def follow(self, request, pk=None):
        target = self.get_object()

        if request.method == "POST":
            if target == request.user:
                return Response(
                    {"detail": "You cannot follow yourself"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            _, created = Follow.objects.get_or_create(
                follower=request.user,
                following=target
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
