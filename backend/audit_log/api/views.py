from audit_log.selectors import AuditLogSelector
from audit_log.serializers import AuditLogSerializer
from rest_framework import response, status, views
from workspace.services import WorkspaceService


class WorkspaceAuditLogListApi(views.APIView):
    def get(self, request, workspace_id):
        # Ensure user has access to workspace
        WorkspaceService.get_workspace_for_user_with_role(
            user=request.user,
            workspace_id=workspace_id
        )

        filters = {}
        if "action" in request.query_params:
            filters["action"] = request.query_params["action"]
        if "user_id" in request.query_params:
            filters["user_id"] = request.query_params["user_id"]

        logs = AuditLogSelector.list_logs_for_workspace(
            workspace_id=workspace_id,
            filters=filters
        )

        # Using default pagination defined in core
        page = self.paginate_queryset(logs)
        if page is not None:
            serializer = AuditLogSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = AuditLogSerializer(logs, many=True)
        return response.Response(serializer.data, status=status.HTTP_200_OK)

    @property
    def paginator(self):
        if not hasattr(self, '_paginator'):
            from core.pagination import DefaultPagination
            self._paginator = DefaultPagination()
        return self._paginator

    def paginate_queryset(self, queryset):
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        return self.paginator.get_paginated_response(data)
