from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import User, Follow
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    UserListSerializer, FollowSerializer, PasswordChangeSerializer
)


class UserRegistrationView(generics.CreateAPIView):
    """Регистрация пользователей"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    """Вход пользователей"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Просмотр и редактирование профиля"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserDetailView(generics.RetrieveAPIView):
    """Просмотр профиля другого пользователя"""
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = 'username'

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class UserListView(generics.ListAPIView):
    """Список пользователей"""
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserListSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['username', 'first_name', 'last_name']
    ordering_fields = ['username', 'created_at']
    ordering = ['-created_at']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class FollowView(APIView):
    """Подписка на пользователя"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, username):
        user_to_follow = get_object_or_404(User, username=username)
        
        if user_to_follow == request.user:
            return Response(
                {'error': 'Нельзя подписаться на самого себя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            following=user_to_follow
        )
        
        if created:
            return Response(
                {'message': f'Вы подписались на {username}'},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'message': 'Вы уже подписаны на этого пользователя'},
                status=status.HTTP_200_OK
            )


class UnfollowView(APIView):
    """Отписка от пользователя"""
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, username):
        user_to_unfollow = get_object_or_404(User, username=username)
        
        try:
            follow = Follow.objects.get(
                follower=request.user,
                following=user_to_unfollow
            )
            follow.delete()
            return Response(
                {'message': f'Вы отписались от {username}'},
                status=status.HTTP_200_OK
            )
        except Follow.DoesNotExist:
            return Response(
                {'error': 'Вы не подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )


class FollowersListView(generics.ListAPIView):
    """Список подписчиков пользователя"""
    serializer_class = FollowSerializer
    
    def get_queryset(self):
        username = self.kwargs['username']
        user = get_object_or_404(User, username=username)
        return Follow.objects.filter(following=user)


class FollowingListView(generics.ListAPIView):
    """Список подписок пользователя"""
    serializer_class = FollowSerializer
    
    def get_queryset(self):
        username = self.kwargs['username']
        user = get_object_or_404(User, username=username)
        return Follow.objects.filter(follower=user)


class PasswordChangeView(APIView):
    """Смена пароля"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({'message': 'Пароль успешно изменен'})


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def refresh_token(request):
    """Обновление токена"""
    try:
        refresh_tokens = request.data['refresh']
        token = RefreshToken(refresh_tokens)
        
        return Response({
            'access': str(token.access_token)
        })
    except Exception as e:
        return Response(
            {'error': 'Недействительный refresh token'},
            status=status.HTTP_400_BAD_REQUEST
        )
