from tasks.models import Task


def get_active_tasks(*, user, project_id, filters=None):
    from django.db.models import Q
    from workspace.services import WorkspaceService

    filters = filters or {}

    # Ensure user has access to workspace
    task_project = Task.objects.filter(project_id=project_id).values("project__workspace_id").first()
    if task_project:
        WorkspaceService.get_workspace_for_user_with_role(
            user=user,
            workspace_id=task_project["project__workspace_id"]
        )

    queryset = Task.objects.filter(
        project_id=project_id,
        is_active=True,
        project__is_active=True,
        project__workspace__is_active=True,
    ).select_related("project", "assignee")

    if status := filters.get("status"):
        queryset = queryset.filter(status=status)

    if assignee := filters.get("assignee"):
        queryset = queryset.filter(assignee_id=assignee)

    if priority := filters.get("priority"):
        queryset = queryset.filter(priority=priority)

    if due_date := filters.get("due_date"):
        queryset = queryset.filter(due_date=due_date)

    if search := filters.get("search"):
        queryset = queryset.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )

    return queryset


def get_active_task_by_id(*, user, task_id):
    from core.exceptions import PermissionException
    from tasks.services import TaskService
    try:
        return TaskService.get_task_for_user(user=user, task_id=task_id)
    except PermissionException:
        return None


def get_active_tasks_assigned_to_user(*, assignee, user=None, filters=None):
    from django.db.models import Q
    filters = filters or {}

    base_filters = {
        "assignee": assignee,
        "is_active": True,
        "project__is_active": True,
        "project__workspace__is_active": True,
    }

    if project_id := filters.get("project"):
        base_filters["project_id"] = project_id

    if status := filters.get("status"):
        base_filters["status"] = status

    if priority := filters.get("priority"):
        base_filters["priority"] = priority

    if due_date := filters.get("due_date"):
        base_filters["due_date"] = due_date

    queryset = Task.objects.filter(**base_filters)

    if user:
        queryset = queryset.filter(
            Q(project__workspace__owner=user) |
            Q(project__workspace__memberships__user=user, project__workspace__memberships__is_active=True)
        ).distinct()

    if search := filters.get("search"):
        queryset = queryset.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )

    return queryset.select_related("project")


def get_comments_for_task(*, user, task_id):
    from tasks.models import Comment
    from tasks.services import TaskService

    # This will check for user access to the task/workspace
    TaskService.get_task_for_user(user=user, task_id=task_id)

    return Comment.objects.filter(
        task_id=task_id,
        is_active=True
    ).select_related("author").order_by("created")
