from core.exceptions import (
    ConflictException,
    PermissionException,
    ValidationException,
)
from django.db import IntegrityError, transaction
from django.utils import timezone
from project.models import Project
from workspace.services import WorkspaceService


class ProjectService:
    @staticmethod
    def deactivate_projects(*, workspace_id, deleted_at):
        Project.objects.filter(
            workspace_id=workspace_id,
            is_active=True
        ).update(
            is_active=False,
            deleted_at=deleted_at
        )

    @staticmethod
    @transaction.atomic
    def create_project(*, user, workspace_id, name, description=""):
        name = name.strip()
        if not name:
            raise ValidationException("Project name cannot be empty")

        from workspace.models import WorkspaceMember
        workspace = WorkspaceService.get_workspace_for_user_with_role(
            user=user,
            workspace_id=workspace_id,
            minimum_role=WorkspaceMember.Role.ADMIN,
        )

        try:
            project = Project.objects.create(
                workspace=workspace,
                name=name,
                description=description,
            )

            from audit_log.services import create_audit_log
            create_audit_log(
                user=user,
                workspace=workspace,
                action="PROJECT_CREATED",
                target_object=project,
                description=f"Project '{project.name}' created"
            )

            return project
        except IntegrityError as err:
            raise ConflictException("Project with this name already exists") from err

    @staticmethod
    def get_project_for_user(*, user, project_id):
        try:
            project = Project.objects.select_related("workspace").get(
                id=project_id,
                is_active=True,
                workspace__is_active=True,
            )
        except Project.DoesNotExist:
            raise PermissionException("Project not found") from None

        # Check workspace access
        WorkspaceService.get_workspace_for_user_with_role(
            user=user,
            workspace_id=project.workspace_id,
        )
        return project

    @staticmethod
    @transaction.atomic
    def update_project(*, user, project_id, name, description):
        from workspace.models import WorkspaceMember
        # Project update requires Admin role in workspace
        project = ProjectService.get_project_for_user(
            user=user,
            project_id=project_id,
        )
        WorkspaceService.get_workspace_for_user_with_role(
            user=user,
            workspace_id=project.workspace_id,
            minimum_role=WorkspaceMember.Role.ADMIN,
        )

        if name is not None:
            name = name.strip()
            if not name:
                raise ValidationException("Project name cannot be empty")
            project.name = name

        if description is not None:
            project.description = description

        project.save()
        return project

    @staticmethod
    @transaction.atomic
    def delete_project(*, user, project_id):
        from tasks.services import TaskService
        from workspace.models import WorkspaceMember

        # Project deletion requires Admin role in workspace
        project = ProjectService.get_project_for_user(
            user=user,
            project_id=project_id,
        )
        WorkspaceService.get_workspace_for_user_with_role(
            user=user,
            workspace_id=project.workspace_id,
            minimum_role=WorkspaceMember.Role.ADMIN,
        )

        deleted_at = timezone.now()

        # 1. Deactivate tasks
        TaskService.deactivate_tasks(project_id=project_id, deleted_at=deleted_at)

        # 2. Deactivate project
        project.is_active = False
        project.deleted_at = deleted_at
        project.save(update_fields=["is_active", "deleted_at", "updated"])
