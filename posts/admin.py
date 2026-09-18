from django.contrib import admin
from .models import Post, Comment, Like, Notification


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['author', 'content_preview', 'likes_count', 'created_at']
    search_fields = ['author__username', 'content']
    list_filter = ['created_at']

    def content_preview(self, obj):
        return obj.content[:60]
    content_preview.short_description = 'Contenu'

    def likes_count(self, obj):
        return obj.likes.count()
    likes_count.short_description = 'Likes'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'content', 'created_at']
    search_fields = ['author__username', 'content']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'sender', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read']
