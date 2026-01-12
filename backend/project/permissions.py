from rest_framework.permissions import BasePermission
from project.models import Project


class IsProjectOwner(BasePermission):
    message = "Permission Denied"

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, Project):
            return False
        return obj.owner_id == request.user.id
