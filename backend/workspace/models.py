import uuid

from core.models.base import BaseModel
from django.conf import settings
from django.db import models


class WorkspaceMember(BaseModel):
    class Role(models.TextChoices):
        OWNER = "OWNER", "Owner"
        ADMIN = "ADMIN", "Admin"
        MEMBER = "MEMBER", "Member"

    workspace = models.ForeignKey(
        "workspace.Workspace",
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="workspace_memberships",
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.MEMBER,
    )
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_invitations",
    )

    class Meta:
        db_table = "workspace_members"
        constraints = [
            models.UniqueConstraint(
                fields=["workspace", "user"],
                condition=models.Q(is_active=True),
                name="unique_active_workspace_member",
            )
        ]

    def __str__(self):
        return f"{self.user.email} - {self.workspace.name} ({self.role})"


class Workspace(BaseModel):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_workspaces",
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="workspace.WorkspaceMember",
        through_fields=("workspace", "user"),
        related_name="joined_workspaces",
        blank=True,
    )

    class Meta:
        db_table = "workspaces"
        indexes = [
            models.Index(fields=["owner"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "name"],
                condition=models.Q(is_active=True),
                name="unique_active_workspace_per_owner",
            )
        ]

    def __str__(self):
        return self.name


class WorkspaceInvitation(BaseModel):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACCEPTED = "ACCEPTED", "Accepted"
        EXPIRED = "EXPIRED", "Expired"
        REVOKED = "REVOKED", "Revoked"

    workspace = models.ForeignKey(
        "workspace.Workspace",
        on_delete=models.CASCADE,
        related_name="invitations",
    )
    email = models.EmailField()
    role = models.CharField(
        max_length=20,
        choices=WorkspaceMember.Role.choices,
        default=WorkspaceMember.Role.MEMBER,
    )
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_workspace_invitations",
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    expires_at = models.DateTimeField()

    class Meta:
        db_table = "workspace_invitations"
        indexes = [
            models.Index(fields=["token"]),
            models.Index(fields=["email", "status"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["workspace", "email"],
                condition=models.Q(status="PENDING"),
                name="unique_pending_invitation_per_workspace",
            )
        ]

    def __str__(self):
        return f"Invite to {self.email} for {self.workspace.name} ({self.status})"

    def is_expired(self):
        from django.utils import timezone
        return self.expires_at < timezone.now()
