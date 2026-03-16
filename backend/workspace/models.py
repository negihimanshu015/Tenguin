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
