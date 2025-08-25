from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Post(models.Model):
    """Модель поста"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name=_('автор')
    )
    image = models.ImageField(
        _('изображение'),
        upload_to='posts/%Y/%m/%d/'
    )
    caption = models.TextField(_('описание'), blank=True, max_length=2200)
    location = models.CharField(_('местоположение'), max_length=100, blank=True)
    
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('дата обновления'), auto_now=True)

    class Meta:
        verbose_name = _('Пост')
        verbose_name_plural = _('Посты')
        db_table = 'posts'
        ordering = ['-created_at']

    def __str__(self):
        return f"Пост от {self.author.username} - {self.created_at.strftime('%d.%m.%Y %H:%M')}"

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def comments_count(self):
        return self.comments.count()


class Like(models.Model):
    """Модель лайков"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name=_('пользователь')
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name=_('пост')
    )
    created_at = models.DateTimeField(_('дата лайка'), auto_now_add=True)

    class Meta:
        verbose_name = _('Лайк')
        verbose_name_plural = _('Лайки')
        db_table = 'likes'
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user.username} лайкнул пост {self.post.id}"


class Comment(models.Model):
    """Модель комментариев"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('автор')
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('пост')
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name=_('родительский комментарий')
    )
    text = models.TextField(_('текст'), max_length=500)
    
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('дата обновления'), auto_now=True)

    class Meta:
        verbose_name = _('Комментарий')
        verbose_name_plural = _('Комментарии')
        db_table = 'comments'
        ordering = ['created_at']

    def __str__(self):
        return f"Комментарий от {self.author.username} к посту {self.post.id}"

    @property
    def replies_count(self):
        return self.replies.count()


class Story(models.Model):
    """Модель историй (Stories)"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='stories',
        verbose_name=_('автор')
    )
    image = models.ImageField(
        _('изображение'),
        upload_to='stories/%Y/%m/%d/'
    )
    text = models.CharField(_('текст'), max_length=200, blank=True)
    
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    expires_at = models.DateTimeField(_('дата истечения'))

    class Meta:
        verbose_name = _('История')
        verbose_name_plural = _('Истории')
        db_table = 'stories'
        ordering = ['-created_at']

    def __str__(self):
        return f"История от {self.author.username} - {self.created_at.strftime('%d.%m.%Y %H:%M')}"

    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at
