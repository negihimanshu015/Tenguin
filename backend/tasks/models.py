from core.models import BaseModel
from django.conf import settings
from django.db import models
from project.models import Project


class Task(BaseModel):
    class Status(models.IntegerChoices):
        TODO = 1, "To Do"
        IN_PROGRESS = 2, "In Progress"
        DONE = 3, "Done"
        BLOCKED = 4, "Blocked"

    class Priority(models.IntegerChoices):
        LOW = 1, "Low"
        MEDIUM = 2, "Medium"
        HIGH = 3, "High"
        URGENT = 4, "Urgent"

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
    status = models.PositiveSmallIntegerField(
        choices=Status.choices,
        default=Status.TODO,
    )
    priority = models.PositiveSmallIntegerField(
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )
    due_date = models.DateField(null=True, blank=True)
    ordering = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "tasks"
        ordering = ["ordering", "due_date", "-priority", "id"]
        indexes = [
            models.Index(fields=["project"]),
            models.Index(fields=["assignee"]),
            models.Index(fields=["status"]),
            models.Index(fields=["priority"]),
            models.Index(fields=["due_date"]),
            models.Index(fields=["ordering"]),
        ]

    def __str__(self):
        return self.title


class Comment(BaseModel):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="task_comments",
    )
    content = models.TextField()

    class Meta:
        db_table = "task_comments"
        ordering = ["created"]

    def __str__(self):
        return f"Comment by {self.author} on {self.task}"
