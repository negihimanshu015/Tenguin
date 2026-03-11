from project.models import Project


def get_active_project(*, owner):
    return Project.objects.filter(
        workspace__owner=owner,
        is_active=True,
    ).select_related("workspace").order_by("-created")

def get_active_project_by_id(*, owner, project_id):
    return Project.objects.filter(
        id=project_id,
        workspace__owner=owner,
        is_active=True,
    ).select_related("workspace").first()
