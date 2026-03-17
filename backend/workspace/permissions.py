from rest_framework.permissions import BasePermission
from workspace.models import Workspace, WorkspaceMember


class IsWorkspaceOwner(BasePermission):
    """
    Strict ownership permission. Only the user who created the workspace.
    """
    message = "Only the workspace owner can perform this action."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        workspace = obj if isinstance(obj, Workspace) else getattr(obj, "workspace", None)
        if not workspace:
            return False
        return workspace.owner_id == request.user.id


class IsWorkspaceAdmin(BasePermission):
    """
    Allows Owner and Admin roles.
    """
    message = "Admin or Owner permissions required."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        workspace = obj if isinstance(obj, Workspace) else getattr(obj, "workspace", None)
        if not workspace:
            return False

        if workspace.owner_id == request.user.id:
            return True

        return workspace.memberships.filter(
            user=request.user,
            role__in=[WorkspaceMember.Role.OWNER, WorkspaceMember.Role.ADMIN],
            is_active=True
        ).exists()


class IsWorkspaceMember(BasePermission):
    """
    Allows Owner, Admin, and Member roles.
    """
    message = "Workspace membership required."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        workspace = obj if isinstance(obj, Workspace) else getattr(obj, "workspace", None)
        if not workspace:
            return False

        if workspace.owner_id == request.user.id:
            return True

        return workspace.memberships.filter(
            user=request.user,
            is_active=True
        ).exists()
