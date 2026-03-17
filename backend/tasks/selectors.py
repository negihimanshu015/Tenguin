from tasks.models import Task


def get_active_tasks(*, user, project_id):
    from workspace.services import WorkspaceService
    # Ensure user has access to workspace
    task_project = Task.objects.filter(project_id=project_id).values("project__workspace_id").first()
    if task_project:
        WorkspaceService.get_workspace_for_user_with_role(
            user=user,
            workspace_id=task_project["project__workspace_id"]
        )

    return Task.objects.filter(
        project_id=project_id,
        is_active=True,
        project__is_active=True,
        project__workspace__is_active=True,
    ).select_related("project", "assignee")


def get_active_task_by_id(*, user, task_id):
    from core.exceptions import PermissionException
    from tasks.services import TaskService
    try:
        return TaskService.get_task_for_user(user=user, task_id=task_id)
    except PermissionException:
        return None


def get_active_tasks_assigned_to_user(*, assignee, user=None):
    from django.db.models import Q
    filters = {
        "assignee": assignee,
        "is_active": True,
        "project__is_active": True,
        "project__workspace__is_active": True,
    }
    queryset = Task.objects.filter(**filters)
    if user:
        queryset = queryset.filter(
            Q(project__workspace__owner=user) |
            Q(project__workspace__memberships__user=user, project__workspace__memberships__is_active=True)
        ).distinct()

    return queryset.select_related("project")
