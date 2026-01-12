from django.conf import settings
from django.db import models
from core.models import BaseModel
from project.models import Project


class Task(BaseModel):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)

    class Meta:
        db_table = "tasks"
        indexes = [
            models.Index(fields=["project"]),
            models.Index(fields=["assignee"]),
            models.Index(fields=["is_completed"]),
        ]

    def __str__(self):
        return self.title
