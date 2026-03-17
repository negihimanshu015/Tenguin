from core.exceptions import (
    PermissionException,
    ValidationException,
)
from django.db import models, transaction
from project.services import ProjectService
from tasks.models import Task


class TaskService:
    @staticmethod
    def deactivate_tasks(*, project_id=None, workspace_id=None, deleted_at):
        filters = models.Q(is_active=True)
        if project_id:
            filters &= models.Q(project_id=project_id)
        if workspace_id:
            filters &= models.Q(project__workspace_id=workspace_id)

        Task.objects.filter(filters).update(
            is_active=False,
            deleted_at=deleted_at
        )

    @staticmethod
    @transaction.atomic
    def create_task(
        *,
        user,
        project_id,
        title,
        description="",
        assignee_id=None,
        status=None,
        priority=None,
        due_date=None,
        ordering=0
    ):
        title = title.strip()
        if not title:
            raise ValidationException("Task title cannot be empty")

        # Task creation requires project access (Member role in workspace)
        project = ProjectService.get_project_for_user(
            user=user,
            project_id=project_id,
        )

        create_kwargs = {
            "project": project,
            "title": title,
            "description": description,
            "ordering": ordering,
        }

        if assignee_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                assignee = User.objects.get(id=assignee_id, is_active=True)
                create_kwargs["assignee"] = assignee
            except User.DoesNotExist:
                raise ValidationException("Assignee not found") from None

        if status is not None:
            create_kwargs["status"] = status
        if priority is not None:
            create_kwargs["priority"] = priority
        if due_date is not None:
            create_kwargs["due_date"] = due_date

        return Task.objects.create(**create_kwargs)

    @staticmethod
    @transaction.atomic
    def update_task(*, user, task_id, **kwargs):
        task = TaskService.get_task_for_user(user=user, task_id=task_id)

        # Handle title specifically for naming rules
        if "title" in kwargs and kwargs["title"] is not None:
            title = kwargs["title"].strip()
            if not title:
                raise ValidationException("Task title cannot be empty")
            task.title = title

        # Handle assignee specifically for object fetching
        if "assignee_id" in kwargs and kwargs["assignee_id"] is not None:
            if kwargs["assignee_id"]:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                try:
                    task.assignee = User.objects.get(id=kwargs["assignee_id"], is_active=True)
                except User.DoesNotExist:
                    raise ValidationException("Assignee not found") from None
            else:
                task.assignee = None

        # Handle other simple fields
        fields = ["description", "status", "priority", "due_date", "ordering"]
        for field in fields:
            if field in kwargs and kwargs[field] is not None:
                setattr(task, field, kwargs[field])

        task.save()
        return task

    @staticmethod
    def get_task_for_user(*, user, task_id):
        try:
            task = Task.objects.select_related("project__workspace").get(
                id=task_id,
                is_active=True,
                project__is_active=True,
                project__workspace__is_active=True,
            )
        except Task.DoesNotExist:
            raise PermissionException("Task not found") from None

        # Check membership in the workspace
        from workspace.services import WorkspaceService
        WorkspaceService.get_workspace_for_user_with_role(
            user=user,
            workspace_id=task.project.workspace_id,
        )
        return task

    @staticmethod
    @transaction.atomic
    def delete_task(*, user, task_id):
        task = TaskService.get_task_for_user(
            user=user,
            task_id=task_id,
        )

        task.is_active = False
        task.save()
