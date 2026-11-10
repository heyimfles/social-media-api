from rest_framework import serializers

from social.models import (
    Post,
    Comment,
    Like,
)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="username",
    )

    class Meta:
        model = Comment
        fields = (
            "id",
            "content",
            "author",
            "created_at",
        )


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            "content",
        )


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "content",
            "hashtags",
            "image",
            "created_at",
        )


class PostListSerializer(serializers.ModelSerializer):
    comments_count = serializers.IntegerField(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    author = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="username",
    )

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "hashtags",
            "image",
            "author",
            "created_at",
            "comments_count",
            "likes_count",
        )


class PostDetailSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    likes = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="author__username",
    )

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "content",
            "hashtags",
            "image",
            "created_at",
            "comments",
            "likes",
        )


class LikeSerializer(serializers.ModelSerializer):
    post = PostSerializer(
        many=False,
        read_only=True,
    )

    class Meta:
        model = Like
        fields = (
            "id",
            "author",
            "post",
        )
