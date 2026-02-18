import pytest

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from project.models import Project
from tasks.models import Task

User = get_user_model()


@pytest.mark.django_db
class TestTaskAPI:

    def setup_method(self):
        self.client = APIClient()

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_list_tasks_for_project(self):
        owner = User.objects.create_user(email="owner@test.com", clerk_id="user_123")
        self.authenticate(owner)

        project = Project.objects.create(owner=owner, name="Project")
        Task.objects.create(project=project, title="Task 1")
        Task.objects.create(project=project, title="Task 2")

        response = self.client.get(f"/api/v1/projects/{project.id}/tasks/")

        assert response.status_code == 200
        assert response.data["meta"]["total_items"] == 2
        assert len(response.data["data"]) == 2

    def test_create_task(self):
        owner = User.objects.create_user(email="owner@test.com", clerk_id="user_123")
        self.authenticate(owner)

        project = Project.objects.create(owner=owner, name="Project")

        response = self.client.post(
            f"/api/v1/projects/{project.id}/tasks/",
            data={"title": "New Task", "description": "Desc"},
            format="json",
        )

        assert response.status_code == 201
        assert response.data["data"]["title"] == "New Task"

    def test_get_task_detail(self):
        owner = User.objects.create_user(email="owner@test.com", clerk_id="user_123")
        self.authenticate(owner)

        project = Project.objects.create(owner=owner, name="Project")
        task = Task.objects.create(project=project, title="Task")

        response = self.client.get(
            f"/api/v1/projects/{project.id}/tasks/{task.id}/"
        )

        assert response.status_code == 200
        assert response.data["data"]["id"] == str(task.id)

    def test_update_task(self):
        owner = User.objects.create_user(email="owner@test.com", clerk_id="user_123")
        self.authenticate(owner)

        project = Project.objects.create(owner=owner, name="Project")
        task = Task.objects.create(project=project, title="Old")

        response = self.client.put(
            f"/api/v1/projects/{project.id}/tasks/{task.id}/",
            data={"title": "Updated", "description": "Updated desc"},
            format="json",
        )

        assert response.status_code == 200
        assert response.data["data"]["title"] == "Updated"

    def test_delete_task(self):
        owner = User.objects.create_user(email="owner@test.com", clerk_id="user_123")
        self.authenticate(owner)

        project = Project.objects.create(owner=owner, name="Project")
        task = Task.objects.create(project=project, title="Task")

        response = self.client.delete(
            f"/api/v1/projects/{project.id}/tasks/{task.id}/"
        )

        assert response.status_code == 200

        task.refresh_from_db()
        assert task.is_active is False

    def test_task_permission_denied(self):
        owner = User.objects.create_user(email="owner@test.com", clerk_id="user_123")
        other = User.objects.create_user(email="other@test.com", clerk_id="user_456")
        self.authenticate(other)

        project = Project.objects.create(owner=owner, name="Project")
        task = Task.objects.create(project=project, title="Task")

        response = self.client.get(
            f"/api/v1/projects/{project.id}/tasks/{task.id}/"
        )

        assert response.status_code == 403

    def test_assigned_to_me_tasks(self):
        owner = User.objects.create_user(email="owner@test.com", clerk_id="user_123")
        assignee = User.objects.create_user(email="assignee@test.com", clerk_id="user_456")
        self.authenticate(assignee)

        project = Project.objects.create(owner=owner, name="Project")

        Task.objects.create(
            project=project,
            title="Assigned Task",
            assignee=assignee,
        )
        Task.objects.create(
            project=project,
            title="Other Task",
        )

        response = self.client.get("/api/v1/tasks/assigned-to-me/")

        assert response.status_code == 200
        assert response.data["meta"]["total_items"] == 1
        assert response.data["data"][0]["title"] == "Assigned Task"
