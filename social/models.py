import os
import uuid
from datetime import datetime

from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import F, Q
from django.utils.text import slugify


def post_image_file_path(instance, filename):
    _, ext = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/posts_images/", filename)


class Follow(models.Model):
    follower = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="following",
    )
    following = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="followers",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "following"], name="unique_follow"
            ),
            models.CheckConstraint(
                condition=~Q(follower=F("following")), name="prevent_self_follow"
            ),
        ]

    def __str__(self):
        return f"{self.follower} -> {self.following}"


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField(help_text="Create a post . . .")
    hashtags = models.CharField(max_length=255)
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="posts",
    )
    image = models.ImageField(
        null=True,
        blank=True,
        upload_to=post_image_file_path,
    )
    published_at = models.DateTimeField(
        default=datetime.now,
    )
    is_published = models.BooleanField(
        default=True,
    )

    def __str__(self):
        return f"{self.title}, {self.author}"


class Comment(models.Model):
    content = models.CharField(max_length=255)
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="comments",
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment of {self.author} to post {self.post.title}"


class Like(models.Model):
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="likes",
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="likes",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["author", "post"], name="unique_like")
        ]

    def __str__(self):
        return f"{self.author} liked {self.post.title}"
