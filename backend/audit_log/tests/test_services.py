import pytest
from audit_log.models import AuditLog
from audit_log.services import create_audit_log
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from project.models import Project
from tasks.models import Task
from workspace.models import Workspace

User = get_user_model()

@pytest.mark.django_db
def test_create_audit_log():
    # Setup
    user = User.objects.create_user(email="test@example.com", clerk_id="user_123", password="password")
    workspace = Workspace.objects.create(name="Test Workspace", owner=user)
    project = Project.objects.create(name="Test Project", workspace=workspace)
    task = Task.objects.create(title="Test Task", project=project)

    # Execute
    action = "TASK_CREATED"
    description = "Task created"
    metadata = {"key": "value"}

    log = create_audit_log(
        user=user,
        workspace=workspace,
        project=project,
        action=action,
        target_object=task,
        description=description,
        metadata=metadata
    )

    # Assert
    assert AuditLog.objects.count() == 1
    assert log.user == user
    assert log.workspace == workspace
    assert log.project == project
    assert log.action == action
    assert log.description == description
    assert log.metadata == metadata
    assert log.content_object == task
    assert log.content_type == ContentType.objects.get_for_model(Task)
    assert log.object_id == task.id
