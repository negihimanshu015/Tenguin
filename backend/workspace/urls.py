from django.urls import path
from workspace.api.views import (
    WorkspaceDetailView,
    WorkspaceListCreateView,
    WorkspaceMemberAddRemoveView,
    WorkspaceMemberListView,
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
    path(
        "<uuid:workspace_id>/members/",
        WorkspaceMemberListView.as_view(),
        name="workspace-members-list",
    ),
    path(
        "<uuid:workspace_id>/members/manage/",
        WorkspaceMemberAddRemoveView.as_view(),
        name="workspace-members-manage",
    ),
]
