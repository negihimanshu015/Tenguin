from audit_log.api.views import WorkspaceAuditLogListApi
from django.urls import path

urlpatterns = [
    path('workspaces/<uuid:workspace_id>/logs/', WorkspaceAuditLogListApi.as_view(), name='workspace-audit-logs'),
]
