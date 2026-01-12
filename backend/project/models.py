from django.conf import settings
from django.db import models
from core.models.base import BaseModel


class Project(BaseModel):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="projects",
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "projects"
        indexes = [
            models.Index(fields=["owner"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "name"],
                condition=models.Q(is_active=False),
                name="unique_active_project_per_owner",
            )
        ]

    def __str__(self):
        return self.name
