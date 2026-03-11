from django.urls import path
from workspace.api.views import (
    WorkspaceDetailView,
    WorkspaceListCreateView,
)

urlpatterns = [
    path(
        "",
        WorkspaceListCreateView.as_view(),
        name="workspace-list",
    ),
    path(
        "<uuid:workspace_id>/",
        WorkspaceDetailView.as_view(),
        name="workspace-detail",
    ),
]
