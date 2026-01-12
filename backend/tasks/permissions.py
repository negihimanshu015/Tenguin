from rest_framework.permissions import BasePermission
from tasks.models import Task


class IsTaskProjectOwner(BasePermission):
    message = "Permission Denied"

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, Task):
            return False
        return obj.project.owner_id == request.user.id
