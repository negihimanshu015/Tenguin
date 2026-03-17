import pytest
from django.contrib.auth import get_user_model
from project.models import Project
from tasks.models import Task
from tasks.selectors import (
    get_active_task_by_id,
    get_active_tasks,
    get_active_tasks_assigned_to_user,
)
from workspace.models import Workspace

User = get_user_model()


@pytest.mark.django_db
class TestTaskSelectors:

    def test_get_active_tasks_returns_only_project_tasks_for_owner(self):
        owner = User.objects.create_user(email="owner@test.com", clerk_id="user_123")
        other = User.objects.create_user(email="other@test.com", clerk_id="user_456")

        ws_owner = Workspace.objects.create(owner=owner, name="WS")
        ws_other = Workspace.objects.create(owner=other, name="Other WS")

        project = Project.objects.create(workspace=ws_owner, name="Project")
        other_project = Project.objects.create(workspace=ws_other, name="Other Project")

        task1 = Task.objects.create(project=project, title="Task 1")
        Task.objects.create(project=other_project, title="Other Task")

        tasks = get_active_tasks(user=owner, project_id=project.id)

        assert tasks.count() == 1
        assert task1 in tasks

    def test_get_active_tasks_excludes_soft_deleted(self):
        owner = User.objects.create_user(email="owner@test.com", clerk_id="user_123")
        ws = Workspace.objects.create(owner=owner, name="WS")
        project = Project.objects.create(workspace=ws, name="Project")

        active_task = Task.objects.create(project=project, title="Active Task")
        deleted_task = Task.objects.create(project=project, title="Deleted Task")
        deleted_task.soft_delete()

        tasks = get_active_tasks(user=owner, project_id=project.id)

        assert active_task in tasks
        assert deleted_task not in tasks

    def test_get_active_task_by_id_returns_task_for_owner(self):
        owner = User.objects.create_user(email="owner@test.com", clerk_id="user_123")
        ws = Workspace.objects.create(owner=owner, name="WS")
        project = Project.objects.create(workspace=ws, name="Project")

        task = Task.objects.create(project=project, title="Task")

        result = get_active_task_by_id(
            user=owner,
            task_id=task.id,
        )

        assert result == task

    def test_get_active_task_by_id_returns_none_for_other_owner(self):
        owner = User.objects.create_user(email="owner@test.com", clerk_id="user_123")
        other = User.objects.create_user(email="other@test.com", clerk_id="user_456")

        ws_other = Workspace.objects.create(owner=other, name="WS")
        project = Project.objects.create(workspace=ws_other, name="Project")
        task = Task.objects.create(project=project, title="Task")

        result = get_active_task_by_id(
            user=owner,
            task_id=task.id,
        )

        assert result is None

    def test_get_active_task_by_id_returns_none_if_soft_deleted(self):
        owner = User.objects.create_user(email="owner@test.com", clerk_id="user_123")
        ws = Workspace.objects.create(owner=owner, name="WS")
        project = Project.objects.create(workspace=ws, name="Project")

        task = Task.objects.create(project=project, title="Task")
        task.soft_delete()

        result = get_active_task_by_id(
            user=owner,
            task_id=task.id,
        )

        assert result is None

    def test_get_active_tasks_assigned_to_user(self):
        owner = User.objects.create_user(email="owner@test.com", clerk_id="user_123")
        assignee = User.objects.create_user(
            email="assignee@test.com", clerk_id="user_456"
        )
        ws = Workspace.objects.create(owner=owner, name="WS")

        project = Project.objects.create(workspace=ws, name="Project")

        assigned_task = Task.objects.create(
            project=project,
            title="Assigned Task",
            assignee=assignee,
        )
        Task.objects.create(project=project, title="Unassigned Task")

        tasks = get_active_tasks_assigned_to_user(
            user=owner,
            assignee=assignee,
        )

        assert assigned_task in tasks
        assert tasks.count() == 1
