import pytest
from core.exceptions import (
    PermissionException,
)
from django.contrib.auth import get_user_model
from project.models import Project
from tasks.models import Task
from tasks.services import TaskService

User = get_user_model()


@pytest.mark.django_db
class TestTaskService:

    def test_create_task(self):
        owner = User.objects.create_user(email="owner@test.com", clerk_id="user_123")
        project = Project.objects.create(owner=owner, name="Project")

        task = TaskService.create_task(
            owner=owner,
            project_id=project.id,
            title="Task",
            description="Desc",
            assignee=None,
        )

        assert task.project == project
        assert task.title == "Task"
        assert task.description == "Desc"
        assert task.assignee is None

    def test_create_task_with_assignee(self):
        owner = User.objects.create_user(email="owner@test.com", clerk_id="user_123")
        assignee = User.objects.create_user(
            email="assignee@test.com", clerk_id="user_456"
        )
        project = Project.objects.create(owner=owner, name="Project")

        task = TaskService.create_task(
            owner=owner,
            project_id=project.id,
            title="Task",
            description="",
            assignee=assignee,
        )

        assert task.assignee == assignee

    def test_create_task_permission_denied(self):
        owner = User.objects.create_user(email="owner@test.com", clerk_id="user_123")
        other = User.objects.create_user(email="other@test.com", clerk_id="user_456")
        project = Project.objects.create(owner=other, name="Project")

        with pytest.raises(PermissionException):
            TaskService.create_task(
                owner=owner,
                project_id=project.id,
                title="Task",
                description="",
                assignee=None,
            )

    def test_get_task_for_owner_success(self):
        owner = User.objects.create_user(email="owner@test.com", clerk_id="user_123")
        project = Project.objects.create(owner=owner, name="Project")
        task = Task.objects.create(project=project, title="Task")

        result = TaskService.get_task_for_owner(
            owner=owner,
            task_id=task.id,
        )

        assert result == task

    def test_get_task_for_owner_not_found(self):
        owner = User.objects.create_user(email="owner@test.com", clerk_id="user_123")

        with pytest.raises(PermissionException):
            TaskService.get_task_for_owner(
                owner=owner,
                task_id="00000000-0000-0000-0000-000000000000",
            )

    def test_get_task_for_owner_permission_denied(self):
        owner = User.objects.create_user(email="owner@test.com", clerk_id="user_123")
        other = User.objects.create_user(email="other@test.com", clerk_id="user_456")

        project = Project.objects.create(owner=other, name="Project")
        task = Task.objects.create(project=project, title="Task")

        with pytest.raises(PermissionException):
            TaskService.get_task_for_owner(
                owner=owner,
                task_id=task.id,
            )

    def test_update_task(self):
        owner = User.objects.create_user(email="owner@test.com", clerk_id="user_123")
        project = Project.objects.create(owner=owner, name="Project")
        task = Task.objects.create(project=project, title="Old")

        updated = TaskService.update_task(
            owner=owner,
            task_id=task.id,
            title="New",
            description="Updated",
            assignee=None,
        )

        assert updated.title == "New"
        assert updated.description == "Updated"

    def test_delete_task_soft_delete(self):
        owner = User.objects.create_user(email="owner@test.com", clerk_id="user_123")
        project = Project.objects.create(owner=owner, name="Project")
        task = Task.objects.create(project=project, title="Task")

        TaskService.delete_task(
            owner=owner,
            task_id=task.id,
        )

        task.refresh_from_db()
        assert task.is_active is False
