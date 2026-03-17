from core.exceptions import (
    ConflictException,
    PermissionException,
    ValidationException,
)
from django.db import IntegrityError, transaction
from django.utils import timezone
from workspace.models import Workspace, WorkspaceMember


class WorkspaceService:

    @staticmethod
    @transaction.atomic
    def create_workspace(*, user, name, description=""):
        name = name.strip()
        if not name:
            raise ValidationException("Workspace name cannot be empty")

        try:
             workspace = Workspace.objects.create(
                owner=user,
                name=name,
                description=description,
            )
             # Automatically add owner as OWNER member
             WorkspaceMember.objects.create(
                 workspace=workspace,
                 user=user,
                 role=WorkspaceMember.Role.OWNER,
             )
             return workspace
        except IntegrityError as err:
            raise ConflictException("Workspace with this name already exists") from err

    @staticmethod
    def create_personal_workspace(*, user):
        return WorkspaceService.create_workspace(
            user=user,
            name="Personal Workspace",
            description="Your default personal workspace",
        )

    @staticmethod
    def get_workspace_for_user_with_role(*, user, workspace_id, minimum_role=None):
        """
        Retrieves a workspace if the user has at least the minimum role.
        If minimum_role is None, just checks if user is any active member/owner.
        """
        try:
            workspace = Workspace.objects.get(
                id=workspace_id,
                is_active=True,
            )
        except Workspace.DoesNotExist:
            raise PermissionException("Workspace not found") from None

        if workspace.owner_id == user.id:
            return workspace

        membership = workspace.memberships.filter(user=user, is_active=True).first()
        if not membership:
            raise PermissionException("Access denied")

        if minimum_role:
            # Simple hierarchy: OWNER > ADMIN > MEMBER
            role_hierarchy = {
                WorkspaceMember.Role.OWNER: 3,
                WorkspaceMember.Role.ADMIN: 2,
                WorkspaceMember.Role.MEMBER: 1,
            }
            if role_hierarchy.get(membership.role, 0) < role_hierarchy.get(minimum_role, 0):
                raise PermissionException(f"Action requires at least {minimum_role} role")

        return workspace

    @staticmethod
    @transaction.atomic
    def update_workspace(*, user, workspace_id, name=None, description=None):
        workspace = WorkspaceService.get_workspace_for_user_with_role(
            user=user,
            workspace_id=workspace_id,
            minimum_role=WorkspaceMember.Role.ADMIN,
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
    def delete_workspace(*, user, workspace_id):
        # Only OWNER can delete workspace
        workspace = WorkspaceService.get_workspace_for_user_with_role(
            user=user,
            workspace_id=workspace_id,
            minimum_role=WorkspaceMember.Role.OWNER,
        )

        from project.services import ProjectService
        from tasks.services import TaskService

        deleted_at = timezone.now()

        # 1. Deactivate tasks
        TaskService.deactivate_tasks(workspace_id=workspace_id, deleted_at=deleted_at)

        # 2. Deactivate projects
        ProjectService.deactivate_projects(workspace_id=workspace_id, deleted_at=deleted_at)

        # 3. Deactivate workspace
        workspace.is_active = False
        workspace.deleted_at = deleted_at
        workspace.save(update_fields=["is_active", "deleted_at", "updated"])

    @staticmethod
    @transaction.atomic
    def add_member(*, user, workspace_id, email):
        workspace = WorkspaceService.get_workspace_for_user_with_role(
            user=user,
            workspace_id=workspace_id,
            minimum_role=WorkspaceMember.Role.ADMIN,
        )

        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            user_to_add = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            raise ValidationException(f"User with email {email} not found") from None

        if user_to_add == workspace.owner:
            raise ValidationException("User is already the owner of this workspace")

        if workspace.members.filter(id=user_to_add.id, workspace_memberships__is_active=True).exists():
            raise ConflictException("User is already a member of this workspace")

        # Create or reactivate membership
        membership, created = WorkspaceMember.objects.get_or_create(
            workspace=workspace,
            user=user_to_add,
            defaults={"role": WorkspaceMember.Role.MEMBER, "invited_by": user}
        )
        if not created:
            membership.is_active = True
            membership.invited_by = user
            membership.save()

        return workspace

    @staticmethod
    @transaction.atomic
    def remove_member(*, user, workspace_id, user_id):
        workspace = WorkspaceService.get_workspace_for_user_with_role(
            user=user,
            workspace_id=workspace_id,
            minimum_role=WorkspaceMember.Role.ADMIN,
        )

        try:
            membership = WorkspaceMember.objects.get(
                workspace=workspace,
                user_id=user_id,
                is_active=True
            )
        except WorkspaceMember.DoesNotExist:
            raise ValidationException("User is not a member of this workspace") from None

        if membership.role == WorkspaceMember.Role.OWNER or membership.user == workspace.owner:
            raise ValidationException("Cannot remove the owner from the workspace")

        membership.is_active = False
        membership.save()
        return workspace

    @staticmethod
    @transaction.atomic
    def change_member_role(*, user, workspace_id, user_id, role):
        # Only OWNER can change roles
        workspace = WorkspaceService.get_workspace_for_user_with_role(
            user=user,
            workspace_id=workspace_id,
            minimum_role=WorkspaceMember.Role.OWNER,
        )

        if role not in WorkspaceMember.Role.values:
            raise ValidationException(f"Invalid role: {role}")

        try:
            membership = WorkspaceMember.objects.get(
                workspace=workspace,
                user_id=user_id,
                is_active=True
            )
        except WorkspaceMember.DoesNotExist:
            raise ValidationException("Membership not found") from None

        if membership.user == workspace.owner:
            raise ValidationException("Cannot change the owner's role")

        membership.role = role
        membership.save()
        return workspace
