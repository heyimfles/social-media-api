from django.contrib import admin

from social.models import (
    Follow,
    Post,
    Comment,
    Like
)


admin.site.register(Follow)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Like)
