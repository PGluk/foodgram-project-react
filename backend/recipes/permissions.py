from rest_framework import permissions


class AdminOrAuthorOrReadOnly(permissions.BasePermission):
    NOT_SAFE_METHOD = ['POST', 'PUT', 'PATCH', 'DELETE']

    def has_permission(self, request, view):
        if view.action in permissions.SAFE_METHODS:
            return True

        if view.action in self.NOT_SAFE_METHOD:
            return request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        if view.action in permissions.SAFE_METHODS:
            return True

        if (request.method in self.NOT_SAFE_METHOD
                and not request.user.is_anonymous):
            return (
                    request.user == obj.author
                    or request.user.is_superuser
                    or request.user.is_admin()
            )

