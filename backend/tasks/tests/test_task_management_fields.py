import datetime

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from project.models import Project
from rest_framework.test import APIClient
from tasks.models import Task
from workspace.models import Workspace

User = get_user_model()

@pytest.mark.django_db
class TestTaskManagementFields:

    def setup_method(self):
        self.client = APIClient()
        self.owner = User.objects.create_user(email="owner@test.com", clerk_id="user_123")
        self.ws = Workspace.objects.create(owner=self.owner, name="WS")
        self.project = Project.objects.create(workspace=self.ws, name="Project")
        self.client.force_authenticate(user=self.owner)

    def test_create_task_with_management_fields(self):
        due_date = (timezone.now() + datetime.timedelta(days=1)).date()
        response = self.client.post(
            f"/api/v1/projects/{self.project.id}/tasks/",
            data={
                "title": "Rich Task",
                "status": Task.Status.IN_PROGRESS,
                "priority": Task.Priority.URGENT,
                "due_date": due_date.isoformat(),
                "ordering": 10
            },
            format="json",
        )

        assert response.status_code == 201
        data = response.data["data"]
        assert data["status"] == Task.Status.IN_PROGRESS
        assert data["priority"] == Task.Priority.URGENT
        assert data["due_date"] == due_date.isoformat()
        assert data["ordering"] == 10

    def test_update_task_fields(self):
        task = Task.objects.create(project=self.project, title="Task")

        response = self.client.put(
            f"/api/v1/projects/{self.project.id}/tasks/{task.id}/",
            data={
                "title": "Updated Task",
                "status": Task.Status.DONE,
                "priority": Task.Priority.LOW,
                "ordering": 5
            },
            format="json",
        )

        assert response.status_code == 200
        data = response.data["data"]
        assert data["status"] == Task.Status.DONE
        assert data["priority"] == Task.Priority.LOW
        assert data["ordering"] == 5

    def test_validate_past_due_date(self):
        past_date = (timezone.now() - datetime.timedelta(days=1)).date()
        response = self.client.post(
            f"/api/v1/projects/{self.project.id}/tasks/",
            data={
                "title": "Invalid Date Task",
                "due_date": past_date.isoformat()
            },
            format="json",
        )

        assert response.status_code == 400
        assert "due_date" in response.data["errors"]
        assert "Due date cannot be in the past" in str(response.data["errors"]["due_date"])

    def test_task_sorting_order(self):
        Task.objects.create(project=self.project, title="T1", ordering=2)
        Task.objects.create(project=self.project, title="T2", ordering=1)

        response = self.client.get(f"/api/v1/projects/{self.project.id}/tasks/")

        assert response.status_code == 200
        data = response.data["data"]
        assert data[0]["title"] == "T2"
        assert data[1]["title"] == "T1"
