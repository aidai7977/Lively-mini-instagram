from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import Post, Like, Comment, Story
from apps.accounts.serializers import UserListSerializer


class PostCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания постов"""
    
    class Meta:
        model = Post
        fields = ('image', 'caption', 'location')

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class PostSerializer(serializers.ModelSerializer):
    """Сериализатор для постов"""
    author = UserListSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = (
            'id', 'author', 'image', 'caption', 'location',
            'likes_count', 'comments_count', 'is_liked',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'author', 'created_at', 'updated_at')

    def get_likes_count(self, obj):
        return obj.likes_count

    def get_comments_count(self, obj):
        return obj.comments_count

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(user=request.user, post=obj).exists()
        return False


class PostDetailSerializer(PostSerializer):
    """Детальный сериализатор для постов с комментариями"""
    recent_comments = serializers.SerializerMethodField()

    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + ('recent_comments',)

    def get_recent_comments(self, obj):
        recent_comments = obj.comments.filter(parent=None)[:3]
        return CommentSerializer(recent_comments, many=True, context=self.context).data


class LikeSerializer(serializers.ModelSerializer):
    """Сериализатор для лайков"""
    user = UserListSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ('id', 'user', 'created_at')
        read_only_fields = ('id', 'created_at')


class CommentCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания комментариев"""
    
    class Meta:
        model = Comment
        fields = ('text', 'parent')

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        validated_data['post_id'] = self.context['view'].kwargs['post_pk']
        return super().create(validated_data)

    def validate_parent(self, value):
        if value and value.post_id != int(self.context['view'].kwargs['post_pk']):
            raise serializers.ValidationError("Родительский комментарий должен принадлежать тому же посту")
        return value


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев"""
    author = UserListSerializer(read_only=True)
    replies_count = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            'id', 'author', 'text', 'parent', 'replies_count',
            'replies', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'author', 'created_at', 'updated_at')

    def get_replies_count(self, obj):
        return obj.replies_count

    def get_replies(self, obj):
        if obj.parent is None:  # Показываем ответы только для основных комментариев
            replies = obj.replies.all()[:2]  # Показываем только 2 последних ответа
            return CommentSerializer(replies, many=True, context=self.context).data
        return []


class StoryCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания историй"""
    
    class Meta:
        model = Story
        fields = ('image', 'text')

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        validated_data['expires_at'] = timezone.now() + timedelta(hours=24)
        return super().create(validated_data)


class StorySerializer(serializers.ModelSerializer):
    """Сериализатор для историй"""
    author = UserListSerializer(read_only=True)
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = (
            'id', 'author', 'image', 'text', 'is_expired',
            'created_at', 'expires_at'
        )
        read_only_fields = ('id', 'author', 'created_at', 'expires_at')

    def get_is_expired(self, obj):
        return obj.is_expired
