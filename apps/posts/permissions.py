from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешение только владельцу объекта изменять его.
    Остальные могут только читать.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешения на чтение предоставляются для любого запроса,
        # поэтому мы всегда разрешаем GET, HEAD или OPTIONS запросы.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Разрешения на запись предоставляются только владельцу объекта.
        return obj.author == request.user


class IsCommentOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешение только автору комментария изменять его.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class CanViewPrivateProfile(permissions.BasePermission):
    """
    Разрешение для просмотра приватных профилей.
    Приватный профиль может видеть только сам пользователь или его подписчики.
    """

    def has_object_permission(self, request, view, obj):
        # Если профиль публичный, разрешаем всем
        if not obj.is_private:
            return True
        
        # Если это сам пользователь, разрешаем
        if request.user == obj:
            return True
        
        # Если пользователь подписан на приватный аккаунт
        if request.user.is_authenticated:
            from apps.accounts import Follow
            return Follow.objects.filter(
                follower=request.user,
                following=obj
            ).exists()
        
        return False


class CanViewUserPosts(permissions.BasePermission):
    """
    Разрешение для просмотра постов пользователя.
    Посты приватного пользователя могут видеть только подписчики.
    """

    def has_permission(self, request, view):
        if not hasattr(view, 'get_author'):
            return True
            
        author = view.get_author()
        if not author.is_private:
            return True
            
        if request.user == author:
            return True
            
        if request.user.is_authenticated:
            from apps.accounts import Follow
            return Follow.objects.filter(
                follower=request.user,
                following=author
            ).exists()
            
        return False
