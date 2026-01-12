from django.urls import path
from .api.views import (
    TaskListCreateView,
    TaskDetailView,
    AssignedTaskListView,
)

app_name = "tasks"

urlpatterns = [
    path(
        "projects/<uuid:project_id>/tasks/",
        TaskListCreateView.as_view(),
        name="task-list-create",
    ),
    path(
        "projects/<uuid:project_id>/tasks/<uuid:task_id>/",
        TaskDetailView.as_view(),
        name="task-detail",
    ),
    path(
        "tasks/assigned-to-me/",
        AssignedTaskListView.as_view(),
        name="tasks-assigned-to-me",
    ),
]
