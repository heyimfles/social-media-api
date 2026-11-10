from rest_framework import mixins, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.decorators import action

import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count

from social.models import (
    Post,
    Like,
    Comment,
)
from social.serializers import (
    PostSerializer,
    PostListSerializer,
    PostDetailSerializer,
    CommentCreateSerializer,
)


class PostFilter(django_filters.FilterSet):
    hashtags = django_filters.CharFilter(
        lookup_expr="icontains",
    )

    class Meta:
        model = Post
        fields = (
            "hashtags",
        )


class PostViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = PostFilter


    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=["post", "delete"],
        url_path="like"
    )
    def like(self, request, pk=None):
        post = self.get_object()
        author = self.request.user

        if request.method == "POST":
            _, created = Like.objects.get_or_create(
                post=post,
                author=author,
            )

            if not created:
                return Response(
                    {"detail": "You already liked this post"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                status=status.HTTP_201_CREATED,
            )

        deleted, _ = Like.objects.filter(
            post=post, author=author,
        ).delete()

        if not deleted:
            return Response(
                {"detail": "This post is not in your liked posts"},
            )

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="comment"
    )
    def comment(self, request, pk=None):
        post = self.get_object()
        author = self.request.user

        Comment.objects.get_or_create(
            post=post,
            author=author,
            content=request.data["content"],
        )

        return Response(
            status=status.HTTP_201_CREATED,
        )

    def get_queryset(self):
        queryset = self.queryset

        if self.action == "list":
            queryset = queryset.annotate(
                comments_count=Count(
                    "comments",
                    distinct=True
                ),
                likes_count=Count(
                    "likes",
                    distinct=True
                )
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer

        if self.action == "retrieve":
            return PostDetailSerializer

        if self.action == "like":
            return serializers.Serializer

        if self.action == "comment":
            return CommentCreateSerializer

        return PostSerializer
