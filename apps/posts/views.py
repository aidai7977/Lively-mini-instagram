from rest_framework import status, generics, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone

from .models import Post, Like, Comment, Story
from apps.accounts.models import User, Follow
from .serializers import (
    PostSerializer, PostCreateSerializer, PostDetailSerializer,
    LikeSerializer, CommentSerializer, CommentCreateSerializer,
    StorySerializer, StoryCreateSerializer
)
from .permissions import IsOwnerOrReadOnly, IsCommentOwnerOrReadOnly, CanViewUserPosts


class PostViewSet(ModelViewSet):
    """ViewSet для постов"""
    queryset = Post.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['caption', 'location', 'author__username']
    filterset_fields = ['author', 'location']
    # 'likes_count' является вычисляемым свойством, по нему нельзя сортировать без аннотации
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return PostCreateSerializer
        elif self.action == 'retrieve':
            return PostDetailSerializer
        return PostSerializer

    def get_queryset(self):
        queryset = Post.objects.select_related('author').prefetch_related('likes', 'comments')
        
        # Фильтрация по подпискам (лента новостей)
        if self.action == 'list' and self.request.query_params.get('feed') == 'true':
            if self.request.user.is_authenticated:
                following_users = Follow.objects.filter(
                    follower=self.request.user
                ).values_list('following', flat=True)
                queryset = queryset.filter(author__in=following_users)
            else:
                queryset = queryset.none()
        
        return queryset

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Лайкнуть пост"""
        post = self.get_object()
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        
        if created:
            return Response({'message': 'Пост лайкнут'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Вы уже лайкнули этот пост'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'])
    def unlike(self, request, pk=None):
        """Убрать лайк с поста"""
        post = self.get_object()
        try:
            like = Like.objects.get(user=request.user, post=post)
            like.delete()
            return Response({'message': 'Лайк убран'}, status=status.HTTP_200_OK)
        except Like.DoesNotExist:
            return Response(
                {'error': 'Вы не лайкали этот пост'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def likes(self, request, pk=None):
        """Список пользователей, которые лайкнули пост"""
        post = self.get_object()
        likes = Like.objects.filter(post=post).select_related('user')
        serializer = LikeSerializer(likes, many=True)
        return Response(serializer.data)


class UserPostsViewSet(generics.ListAPIView):
    """Посты конкретного пользователя"""
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated, CanViewUserPosts]
    filter_backends = [OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        username = self.kwargs['username']
        author = get_object_or_404(User, username=username)
        return Post.objects.filter(author=author).select_related('author').prefetch_related('likes', 'comments')

    def get_author(self):
        username = self.kwargs['username']
        return get_object_or_404(User, username=username)


class CommentViewSet(ModelViewSet):
    """ViewSet для комментариев"""
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsCommentOwnerOrReadOnly]
    filter_backends = [OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['created_at']

    def get_queryset(self):
        post_pk = self.kwargs['post_pk']
        return Comment.objects.filter(post_id=post_pk).select_related('author', 'parent')

    def get_serializer_class(self):
        if self.action == 'create':
            return CommentCreateSerializer
        return CommentSerializer

    def perform_create(self, serializer):
        post_pk = self.kwargs['post_pk']
        post = get_object_or_404(Post, pk=post_pk)
        serializer.save(author=self.request.user, post=post)


class StoryViewSet(ModelViewSet):
    """ViewSet для историй"""
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [OrderingFilter]
    ordering = ['-created_at']

    def get_queryset(self):
        # Показываем только активные истории
        return Story.objects.filter(
            expires_at__gt=timezone.now()
        ).select_related('author')

    def get_serializer_class(self):
        if self.action == 'create':
            return StoryCreateSerializer
        return StorySerializer

    @action(detail=False, methods=['get'])
    def following_stories(self, request):
        """Истории от подписок"""
        if request.user.is_authenticated:
            following_users = Follow.objects.filter(
                follower=request.user
            ).values_list('following', flat=True)
            
            stories = Story.objects.filter(
                author__in=following_users,
                expires_at__gt=timezone.now()
            ).select_related('author').order_by('-created_at')
            
            serializer = self.get_serializer(stories, many=True)
            return Response(serializer.data)
        else:
            return Response([])


class FeedView(generics.ListAPIView):
    """Лента новостей (посты от подписок)"""
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering = ['-created_at']

    def get_queryset(self):
        following_users = Follow.objects.filter(
            follower=self.request.user
        ).values_list('following', flat=True)
        
        return Post.objects.filter(
            author__in=following_users
        ).select_related('author').prefetch_related('likes', 'comments')


class ExploreView(generics.ListAPIView):
    """Рекомендуемые посты"""
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering = ['-created_at']

    def get_queryset(self):
        # Исключаем посты от подписок и свои посты
        following_users = Follow.objects.filter(
            follower=self.request.user
        ).values_list('following', flat=True)
        
        excluded_users = list(following_users) + [self.request.user.id]
        
        return Post.objects.exclude(
            author__in=excluded_users
        ).filter(
            author__is_private=False
        ).select_related('author').prefetch_related('likes', 'comments')
