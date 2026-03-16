from core.exceptions import (
    ConflictException,
    PermissionException,
    ValidationException,
)
from django.db import IntegrityError, transaction
from workspace.models import Workspace, WorkspaceMember


class WorkspaceService:

    @staticmethod
    @transaction.atomic
    def create_workspace(*, owner, name, description=""):
        name = name.strip()
        if not name:
            raise ValidationException("Workspace name cannot be empty")

        try:
             workspace = Workspace.objects.create(
                owner=owner,
                name=name,
                description=description,
            )
             # Automatically add owner as OWNER member
             WorkspaceMember.objects.create(
                 workspace=workspace,
                 user=owner,
                 role=WorkspaceMember.Role.OWNER,
             )
             return workspace
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

    @staticmethod
    @transaction.atomic
    def add_member(*, owner, workspace_id, email):
        workspace = WorkspaceService.get_workspace_for_owner(
            owner=owner,
            workspace_id=workspace_id,
        )

        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            user_to_add = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            raise ValidationException(f"User with email {email} not found") from None

        if user_to_add == owner:
            raise ValidationException("You cannot add yourself as a member")

        if workspace.members.filter(id=user_to_add.id, memberships__is_active=True).exists():
            raise ConflictException("User is already a member of this workspace")

        # Create or reactivate membership
        membership, created = WorkspaceMember.objects.get_or_create(
            workspace=workspace,
            user=user_to_add,
            defaults={"role": WorkspaceMember.Role.MEMBER, "invited_by": owner}
        )
        if not created:
            membership.is_active = True
            membership.invited_by = owner
            membership.save()

        return workspace

    @staticmethod
    @transaction.atomic
    def remove_member(*, owner, workspace_id, user_id):
        workspace = WorkspaceService.get_workspace_for_owner(
            owner=owner,
            workspace_id=workspace_id,
        )

        try:
            membership = WorkspaceMember.objects.get(
                workspace=workspace,
                user_id=user_id,
                is_active=True
            )
        except WorkspaceMember.DoesNotExist:
            raise ValidationException("User is not a member of this workspace") from None

        if membership.role == WorkspaceMember.Role.OWNER:
            raise ValidationException("Cannot remove the owner from the workspace")

        membership.soft_delete()
        return workspace
