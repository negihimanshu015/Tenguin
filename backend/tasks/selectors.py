from tasks.models import Task


def get_active_tasks(*, owner, project_id):
    return Task.objects.filter(
        project__id=project_id,
        project__owner=owner,
        is_active=True,
    ).select_related("project", "assignee").order_by("-created")


def get_active_task_by_id(*, owner, task_id):
    return Task.objects.filter(
        id=task_id,
        project__owner=owner,
        is_active=True,
    ).select_related("project", "assignee").first()


def get_active_tasks_assigned_to_user(*, owner, assignee):
    return Task.objects.filter(
        project__owner=owner,
        assignee=assignee,
        is_active=True,
    ).select_related("project").order_by("-created")
