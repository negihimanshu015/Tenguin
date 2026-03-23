from django.db.models import Q
from project.models import Project


def get_active_project(*, user, workspace_id=None):
    filters = Q(is_active=True, workspace__is_active=True)
    if workspace_id:
        filters &= Q(workspace_id=workspace_id)

    return Project.objects.filter(
        filters & (Q(workspace__owner=user) | Q(workspace__memberships__user=user, workspace__memberships__is_active=True))
    ).distinct().order_by("-created")

def get_active_project_by_id(*, user, project_id):
    from core.exceptions import PermissionException
    from project.services import ProjectService
    try:
        return ProjectService.get_project_for_user(user=user, project_id=project_id)
    except PermissionException:
        return None

def get_deleted_projects(*, user, workspace_id):
    from workspace.services import WorkspaceService

    # Verify workspace access
    WorkspaceService.get_workspace_for_user_with_role(
        user=user,
        workspace_id=workspace_id,
    )

    return Project.objects.filter(
        workspace_id=workspace_id,
        is_active=False
    ).order_by("-deleted_at")
