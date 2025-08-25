from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from . import views

app_name = 'posts'

# Основной роутер
router = DefaultRouter()
router.register(r'posts', views.PostViewSet)
router.register(r'stories', views.StoryViewSet)

# Вложенный роутер для комментариев
posts_router = routers.NestedDefaultRouter(router, r'posts', lookup='post')
posts_router.register(r'comments', views.CommentViewSet, basename='post-comments')

urlpatterns = [
    # API роуты
    path('', include(router.urls)),
    path('', include(posts_router.urls)),
    
    # Дополнительные endpoints
    path('feed/', views.FeedView.as_view(), name='feed'),
    path('explore/', views.ExploreView.as_view(), name='explore'),
    path('users/<str:username>/posts/', views.UserPostsViewSet.as_view(), name='user_posts'),
]
