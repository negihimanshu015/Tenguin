from django.urls import path

from .api.views import (
    ProjectDetailView,
    ProjectListCreateView,
    ProjectPermanentDeleteView,
    ProjectRestoreView,
    ProjectTrashListView,
)

app_name = "projects"

urlpatterns = [
    path(
        "",
        ProjectListCreateView.as_view(),
        name="project-list-create",
    ),
    path(
        "<uuid:project_id>/",
        ProjectDetailView.as_view(),
        name="project-detail",
    ),
    path(
        "trash/",
        ProjectTrashListView.as_view(),
        name="project-trash-list",
    ),
    path(
        "<uuid:project_id>/restore/",
        ProjectRestoreView.as_view(),
        name="project-restore",
    ),
    path(
        "<uuid:project_id>/permanent-delete/",
        ProjectPermanentDeleteView.as_view(),
        name="project-permanent-delete",
    ),
]
