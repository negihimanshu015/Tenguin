from django.urls import path

from .api.views import (
    AssignedTaskListView,
    CommentDetailApi,
    CommentListCreateApi,
    TaskDetailView,
    TaskListCreateView,
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
    # Comment Endpoints
    path(
        "tasks/<uuid:task_id>/comments/",
        CommentListCreateApi.as_view(),
        name="comment-list-create",
    ),
    path(
        "comments/<uuid:comment_id>/",
        CommentDetailApi.as_view(),
        name="comment-detail",
    ),
]
