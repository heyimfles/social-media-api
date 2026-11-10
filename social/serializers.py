from django.contrib.auth import get_user_model
from rest_framework import serializers

from social.models import (
    Follow,
    Post,
    Comment,
    Like,
)

class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "content",
            "hashtags",
            "author",
            "created_at",
        )


class CommentSerializer(serializers.ModelSerializer):
    post = PostSerializer(
        many=False,
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = (
            "id",
            "content",
            "author",
            "post",
            "created_at",
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
