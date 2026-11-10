from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count

from social.models import (
    Post
)
from social.serializers import (
    PostSerializer,
    PostListSerializer,
    PostDetailSerializer,
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

        return PostSerializer
