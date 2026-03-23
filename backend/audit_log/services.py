from audit_log.models import AuditLog


def create_audit_log(
    *,
    user,
    workspace,
    action: str,
    target_object=None,
    project=None,
    description: str = "",
    metadata: dict = None
) -> AuditLog:
    if metadata is None:
        metadata = {}

    return AuditLog.objects.create(
        user=user,
        workspace=workspace,
        project=project,
        content_object=target_object,
        action=action,
        description=description,
        metadata=metadata
    )
