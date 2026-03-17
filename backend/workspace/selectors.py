from workspace.models import Workspace


def get_active_workspaces(*, user):
    from django.db.models import Q
    return Workspace.objects.filter(
        Q(owner=user) | Q(memberships__user=user, memberships__is_active=True),
        is_active=True,
    ).distinct().order_by("-created")

def get_active_workspace_by_id(*, user, workspace_id):
    from django.db.models import Q
    return Workspace.objects.filter(
        Q(owner=user) | Q(memberships__user=user, memberships__is_active=True),
        id=workspace_id,
        is_active=True,
    ).distinct().first()

def get_workspace_members(*, user, workspace_id):
    from core.exceptions import PermissionException
    try:
        workspace = Workspace.objects.get(
            id=workspace_id,
            is_active=True
        )
    except Workspace.DoesNotExist:
        raise PermissionException("Workspace not found") from None

    # Check if user is owner or member
    # We check if an active membership exists for the user in this workspace
    if workspace.owner != user and not workspace.memberships.filter(user=user, is_active=True).exists():
        raise PermissionException("Access denied") from None

    return workspace.memberships.filter(is_active=True).select_related("user")
