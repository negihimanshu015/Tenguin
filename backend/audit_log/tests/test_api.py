import pytest
from audit_log.models import AuditLog
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from project.models import Project
from rest_framework.test import APIClient
from tasks.models import Task
from workspace.models import Workspace, WorkspaceMember

User = get_user_model()

@pytest.mark.django_db
def test_workspace_audit_log_list_api():
    # Setup
    user = User.objects.create_user(email="test@example.com", clerk_id="user_123", password="password")
    workspace = Workspace.objects.create(name="Test Workspace", owner=user)
    # Owner should be a member
    WorkspaceMember.objects.create(workspace=workspace, user=user, role=WorkspaceMember.Role.OWNER)

    project = Project.objects.create(name="Test Project", workspace=workspace)
    task = Task.objects.create(title="Test Task", project=project)

    AuditLog.objects.create(
        user=user,
        workspace=workspace,
        action="TEST_ACTION",
        content_type=ContentType.objects.get_for_model(Task),
        object_id=task.id,
        description="Test log entry"
    )

    client = APIClient()
    client.force_authenticate(user=user)

    url = reverse('workspace-audit-logs', kwargs={'workspace_id': str(workspace.id)})

    # Execute
    response = client.get(url)

    # Assert
    assert response.status_code == 200
    assert len(response.data['data']) == 1
    assert response.data['data'][0]['action'] == "TEST_ACTION"
    assert response.data['data'][0]['user_email'] == user.email
