from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Аутентификация
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('refresh/', views.refresh_token, name='refresh_token'),
    
    # Профиль
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/password/', views.PasswordChangeView.as_view(), name='password_change'),
    
    # Пользователи
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<str:username>/', views.UserDetailView.as_view(), name='user_detail'),
    
    # Подписки
    path('users/<str:username>/follow/', views.FollowView.as_view(), name='follow'),
    path('users/<str:username>/unfollow/', views.UnfollowView.as_view(), name='unfollow'),
    path('users/<str:username>/followers/', views.FollowersListView.as_view(), name='followers'),
    path('users/<str:username>/following/', views.FollowingListView.as_view(), name='following'),
]
