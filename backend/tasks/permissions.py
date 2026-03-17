from rest_framework.permissions import BasePermission
from tasks.models import Task


class IsTaskProjectMember(BasePermission):
    """
    Checks if user is a member of the workspace the task's project belongs to.
    """
    message = "You do not have permission to access tasks in this project."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, Task):
            return False

        workspace = obj.project.workspace
        if workspace.owner_id == request.user.id:
            return True

        return workspace.memberships.filter(
            user=request.user,
            is_active=True
        ).exists()
