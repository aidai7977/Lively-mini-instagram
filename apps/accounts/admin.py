from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Follow


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Административная панель для пользователей"""
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'created_at')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_private', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    filter_horizontal = ('groups', 'user_permissions')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Персональная информация'), {
            'fields': ('first_name', 'last_name', 'email', 'bio', 'avatar', 'website')
        }),
        (_('Разрешения'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_private', 'groups', 'user_permissions'),
        }),
        (_('Важные даты'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Административная панель для подписок"""
    list_display = ('follower', 'following', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('follower__username', 'following__username')
    raw_id_fields = ('follower', 'following')
    ordering = ('-created_at',)
