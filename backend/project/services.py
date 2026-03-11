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
    @transaction.atomic
    def create_project(*, owner, workspace_id, name, description=""):
        name = name.strip()
        if not name:
            raise ValidationException("Project name cannot be empty")

        workspace = WorkspaceService.get_workspace_for_owner(
            owner=owner,
            workspace_id=workspace_id,
        )

        try:
             return Project.objects.create(
                workspace=workspace,
                name=name,
                description=description,
            )
        except IntegrityError as err:
            raise ConflictException("Project with this name already exists") from err

    @staticmethod
    def get_project_for_owner(*, owner, project_id):
        try:
            return Project.objects.select_related("workspace").get(
                id=project_id,
                workspace__owner=owner,
                is_active=True,
            )
        except Project.DoesNotExist:
            raise PermissionException("Project not found or access denied") from None

    @staticmethod
    @transaction.atomic
    def update_project(*, owner, project_id, name=None, description=None):
        project = ProjectService.get_project_for_owner(
            owner=owner,
            project_id=project_id,
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
    def delete_project(*, owner, project_id):
        project = ProjectService.get_project_for_owner(
            owner=owner,
            project_id=project_id,
        )

        project.is_active = False
        project.save()
