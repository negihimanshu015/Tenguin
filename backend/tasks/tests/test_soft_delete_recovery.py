import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from project.models import Project
from project.services import ProjectService
from rest_framework import status
from rest_framework.test import APIClient
from tasks.models import Task
from tasks.services import TaskService
from workspace.models import Workspace

User = get_user_model()

@pytest.mark.django_db
class TestSoftDeleteRecovery:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="admin@test.com", clerk_id="admin_123")
        self.client.force_authenticate(user=self.user)
        self.workspace = Workspace.objects.create(owner=self.user, name="WS")
        self.project = Project.objects.create(workspace=self.workspace, name="Project")
        self.task = Task.objects.create(project=self.project, title="Task")

    def test_task_trash_listing(self):
        # Soft delete the task
        TaskService.delete_task(user=self.user, task_id=self.task.id)

        url = reverse("tasks:task-trash-list", kwargs={"project_id": self.project.id})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["meta"]["total_items"] == 1
        assert response.data["data"][0]["id"] == str(self.task.id)

    def test_task_restore(self):
        TaskService.delete_task(user=self.user, task_id=self.task.id)

        url = reverse("tasks:task-restore", kwargs={"project_id": self.project.id, "task_id": self.task.id})
        response = self.client.post(url)

        assert response.status_code == status.HTTP_200_OK
        self.task.refresh_from_db()
        assert self.task.is_active is True
        assert self.task.deleted_at is None

    def test_task_permanent_delete(self):
        TaskService.delete_task(user=self.user, task_id=self.task.id)

        url = reverse("tasks:task-permanent-delete", kwargs={"project_id": self.project.id, "task_id": self.task.id})
        response = self.client.delete(url)

        assert response.status_code == status.HTTP_200_OK
        assert not Task.objects.filter(id=self.task.id).exists()

    def test_project_trash_listing(self):
        ProjectService.delete_project(user=self.user, project_id=self.project.id)

        url = reverse("projects:project-trash-list")
        response = self.client.get(url, {"workspace_id": self.workspace.id})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["meta"]["total_items"] == 1
        assert response.data["data"][0]["id"] == str(self.project.id)

    def test_project_restore(self):
        ProjectService.delete_project(user=self.user, project_id=self.project.id)

        url = reverse("projects:project-restore", kwargs={"project_id": self.project.id})
        response = self.client.post(url)

        assert response.status_code == status.HTTP_200_OK
        self.project.refresh_from_db()
        assert self.project.is_active is True
        assert self.project.deleted_at is None

    def test_project_permanent_delete(self):
        ProjectService.delete_project(user=self.user, project_id=self.project.id)

        url = reverse("projects:project-permanent-delete", kwargs={"project_id": self.project.id})
        response = self.client.delete(url)

        assert response.status_code == status.HTTP_200_OK
        assert not Project.objects.filter(id=self.project.id).exists()
