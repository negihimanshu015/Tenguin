from project.models import Project
from rest_framework.permissions import BasePermission


class IsProjectWorkspaceAdmin(BasePermission):
    """
    Checks if user is an Admin/Owner of the workspace the project belongs to.
    """
    message = "Admin or Owner permissions required for this project."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, Project):
            return False

        workspace = obj.workspace
        if workspace.owner_id == request.user.id:
            return True

        from workspace.models import WorkspaceMember
        return workspace.memberships.filter(
            user=request.user,
            role__in=[WorkspaceMember.Role.OWNER, WorkspaceMember.Role.ADMIN],
            is_active=True
        ).exists()
