from workspace.models import Workspace


def get_active_workspaces(*, owner):
    return Workspace.objects.filter(
        owner=owner,
        is_active=True,
    ).order_by("-created")

def get_active_workspace_by_id(*, owner, workspace_id):
    return Workspace.objects.filter(
        id=workspace_id,
        owner=owner,
        is_active=True,
    ).first()
