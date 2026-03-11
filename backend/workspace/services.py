from core.exceptions import (
    ConflictException,
    PermissionException,
    ValidationException,
)
from django.db import IntegrityError, transaction
from workspace.models import Workspace


class WorkspaceService:

    @staticmethod
    @transaction.atomic
    def create_workspace(*, owner, name, description=""):
        name = name.strip()
        if not name:
            raise ValidationException("Workspace name cannot be empty")

        try:
             return Workspace.objects.create(
                owner=owner,
                name=name,
                description=description,
            )
        except IntegrityError as err:
            raise ConflictException("Workspace with this name already exists") from err

    @staticmethod
    def create_personal_workspace(*, owner):
        return WorkspaceService.create_workspace(
            owner=owner,
            name="Personal Workspace",
            description="Your default personal workspace",
        )

    @staticmethod
    def get_workspace_for_owner(*, owner, workspace_id):
        try:
            return Workspace.objects.get(
                id=workspace_id,
                owner=owner,
                is_active=True,
            )
        except Workspace.DoesNotExist:
            raise PermissionException("Workspace not found or access denied") from None

    @staticmethod
    @transaction.atomic
    def update_workspace(*, owner, workspace_id, name=None, description=None):
        workspace = WorkspaceService.get_workspace_for_owner(
            owner=owner,
            workspace_id=workspace_id,
        )

        if name is not None:
            name = name.strip()
            if not name:
                raise ValidationException("Workspace name cannot be empty")
            workspace.name = name

        if description is not None:
            workspace.description = description

        workspace.save()
        return workspace

    @staticmethod
    @transaction.atomic
    def delete_workspace(*, owner, workspace_id):
        workspace = WorkspaceService.get_workspace_for_owner(
            owner=owner,
            workspace_id=workspace_id,
        )

        workspace.is_active = False
        workspace.save()
