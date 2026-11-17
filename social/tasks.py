from datetime import datetime, timezone
from celery import shared_task, Celery

from social.models import Post


@shared_task
def publish_post(post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return "Post doesn't exist."
    if post.is_published:
        return "Post already published."

    if post.published_at <= datetime.now(timezone.utc):
        post.is_published = True
        post.save(update_fields=["is_published"])
        return "Post is published."

    return "It is not time to publish the post yet."


@shared_task
def check_for_unpublished():
    posts = Post.objects.filter(is_published=False)
    count = 0

    for post in posts:
        if post.published_at <= datetime.now(timezone.utc):
            post.is_published = True
            post.save(update_fields=["is_published"])
            count += 1

    return f"Check is complete. {count} late posts have been published."
