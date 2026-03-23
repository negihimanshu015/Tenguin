from core.exceptions import (
    ConflictException,
    PermissionException,
    ValidationException,
)
from django.db import IntegrityError, transaction
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

        project.soft_delete()

        # Also deactivate tasks
        TaskService.deactivate_tasks(project_id=project_id, deleted_at=project.deleted_at)

        from audit_log.services import create_audit_log
        create_audit_log(
            user=user,
            workspace=project.workspace,
            project=project,
            action="PROJECT_DELETED",
            description=f"Project '{project.name}' moved to trash"
        )

    @staticmethod
    @transaction.atomic
    def restore_project(*, user, project_id):
        from workspace.models import WorkspaceMember
        try:
            project = Project.objects.select_related("workspace").get(
                id=project_id,
                is_active=False
            )
        except Project.DoesNotExist:
            raise ValidationException("Project not found in trash") from None

        # Check if workspace is active
        if not project.workspace.is_active:
            raise ValidationException("Cannot restore project because its workspace is deleted.")

        # Project restore requires Admin role in workspace
        WorkspaceService.get_workspace_for_user_with_role(
            user=user,
            workspace_id=project.workspace_id,
            minimum_role=WorkspaceMember.Role.ADMIN,
        )

        project.restore()

        from audit_log.services import create_audit_log
        create_audit_log(
            user=user,
            workspace=project.workspace,
            project=project,
            action="PROJECT_RESTORED",
            target_object=project,
            description=f"Project '{project.name}' restored"
        )
        return project

    @staticmethod
    @transaction.atomic
    def permanent_delete_project(*, user, project_id):
        from workspace.models import WorkspaceMember
        try:
            project = Project.objects.select_related("workspace").get(
                id=project_id,
                is_active=False
            )
        except Project.DoesNotExist:
            raise ValidationException("Project not found in trash") from None

        # Permanent delete requires Admin role in workspace
        WorkspaceService.get_workspace_for_user_with_role(
            user=user,
            workspace_id=project.workspace_id,
            minimum_role=WorkspaceMember.Role.ADMIN,
        )

        name = project.name
        workspace = project.workspace

        project.delete() # Hard delete

        from audit_log.services import create_audit_log
        create_audit_log(
            user=user,
            workspace=workspace,
            action="PROJECT_PERMANENTLY_DELETED",
            description=f"Project '{name}' permanently deleted"
        )
