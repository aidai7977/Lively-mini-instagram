from django.contrib import admin
from .models import Post, Like, Comment, Story


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Административная панель для постов"""
    list_display = ('id', 'author', 'caption_short', 'location', 'likes_count', 'comments_count', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('author__username', 'caption', 'location')
    raw_id_fields = ('author',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'likes_count', 'comments_count')
    
    def caption_short(self, obj):
        return obj.caption[:50] + '...' if len(obj.caption) > 50 else obj.caption
    caption_short.short_description = 'Описание'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    """Административная панель для лайков"""
    list_display = ('user', 'post', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'post__caption')
    raw_id_fields = ('user', 'post')
    ordering = ('-created_at',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Административная панель для комментариев"""
    list_display = ('author', 'post', 'text_short', 'parent', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('author__username', 'text', 'post__caption')
    raw_id_fields = ('author', 'post', 'parent')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'replies_count')
    
    def text_short(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_short.short_description = 'Текст'


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    """Административная панель для историй"""
    list_display = ('author', 'text', 'created_at', 'expires_at', 'is_expired')
    list_filter = ('created_at', 'expires_at')
    search_fields = ('author__username', 'text')
    raw_id_fields = ('author',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'is_expired')
    
    def is_expired(self, obj):
        return obj.is_expired
    is_expired.boolean = True
    is_expired.short_description = 'Истекла'
