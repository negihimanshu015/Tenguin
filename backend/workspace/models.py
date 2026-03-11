from core.models.base import BaseModel
from django.conf import settings
from django.db import models


class Workspace(BaseModel):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="workspaces",
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

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
