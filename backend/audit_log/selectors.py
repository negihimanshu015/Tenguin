from audit_log.models import AuditLog


class AuditLogSelector:
    @staticmethod
    def list_logs_for_workspace(*, workspace_id, filters=None):
        if filters is None:
            filters = {}

        queryset = AuditLog.objects.filter(workspace_id=workspace_id).select_related("user")

        if "action" in filters:
            queryset = queryset.filter(action=filters["action"])

        if "user_id" in filters:
            queryset = queryset.filter(user_id=filters["user_id"])

        return queryset
