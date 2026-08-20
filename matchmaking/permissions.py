from rest_framework import permissions


class DRFMatchPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == 'create':
            return request.user.is_authenticated and request.user.has_perm('matchmaking.drf_add_match')
        if view.action in ('update', 'partial_update'):
            return request.user.is_authenticated and request.user.has_perm('matchmaking.drf_change_match')
        if view.action == 'destroy':
            return request.user.is_authenticated and request.user.has_perm('matchmaking.drf_delete_match')
        return True

    def has_object_permission(self, request, view, obj):
        if view.action in ('update', 'partial_update', 'destroy'):
            return obj.is_editable_by(request.user)
        return True
