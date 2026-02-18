from django.db import transaction
from core.exceptions import (
    ValidationExceptions,
    PermissionExceptions,
)
from tasks.models import Task
from project.services import ProjectService


class TaskService:

    @staticmethod
    @transaction.atomic
    def create_task(*, owner, project_id, title, description="", assignee=None):
        title = title.strip()
        if not title:
            raise ValidationExceptions("Task title cannot be empty")

        project = ProjectService.get_project_for_owner(
            owner=owner,
            project_id=project_id,
        )

        return Task.objects.create(
            project=project,
            title=title,
            description=description,
            assignee=assignee,
        )

    @staticmethod
    @transaction.atomic
    def update_task(
        *,
        owner,
        task_id,
        title=None,
        description=None,
        assignee=None,
        is_completed=None,
    ):
        task = TaskService.get_task_for_owner(
            owner=owner,
            task_id=task_id,
        )

        if title is not None:
            title = title.strip()
            if not title:
                raise ValidationExceptions("Task title cannot be empty")
            task.title = title

        if description is not None:
            task.description = description

        if assignee is not None:
            task.assignee = assignee

        if is_completed is not None:
            task.is_completed = is_completed

        task.save()
        return task

    @staticmethod
    def get_task_for_owner(*, owner, task_id):
        try:
            return Task.objects.select_related("project").get(
                id=task_id,
                project__owner=owner,
                is_active=True,
            )
        except Task.DoesNotExist:
            raise PermissionExceptions  ("Task not found or access denied")

    @staticmethod
    @transaction.atomic
    def delete_task(*, owner, task_id):
        task = TaskService.get_task_for_owner(
            owner=owner,
            task_id=task_id,
        )

        task.is_active = False
        task.save()
