from project.models import Project

def get_active_project(*, owner):
    return Project.objects.filter(
        owner = owner,
        is_active = True,        
    ).order_by("-created")

def get_active_project_by_id(*, owner, project_id):
    return Project.objects.filter(
        id = project_id,
        owner = owner,
        is_active = True,        
    ).first()

