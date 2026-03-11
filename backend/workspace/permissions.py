from rest_framework.permissions import BasePermission
from workspace.models import Workspace


class IsWorkspaceOwner(BasePermission):
    message = "Permission Denied"

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, Workspace):
            return False
        return obj.owner_id == request.user.id
