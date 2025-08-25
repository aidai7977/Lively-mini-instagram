from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Кастомная модель пользователя"""
    email = models.EmailField(_('email адрес'), unique=True)
    bio = models.TextField(_('биография'), max_length=500, blank=True)
    avatar = models.ImageField(
        _('аватар'),
        upload_to='avatars/',
        blank=True,
        null=True
    )
    website = models.URLField(_('веб-сайт'), blank=True)
    is_private = models.BooleanField(_('приватный аккаунт'), default=False)
    
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('дата обновления'), auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')
        db_table = 'users'

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class Follow(models.Model):
    """Модель подписок"""
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name=_('подписчик')
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name=_('на кого подписан')
    )
    created_at = models.DateTimeField(_('дата подписки'), auto_now_add=True)

    class Meta:
        verbose_name = _('Подписка')
        verbose_name_plural = _('Подписки')
        db_table = 'follows'
        unique_together = ('follower', 'following')
        constraints = [
            models.CheckConstraint(
                check=~models.Q(follower=models.F('following')),
                name='no_self_follow'
            )
        ]

    def __str__(self):
        return f"{self.follower.username} подписан на {self.following.username}"
