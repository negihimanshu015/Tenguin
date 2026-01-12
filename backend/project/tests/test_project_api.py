import pytest

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from project.models import Project

User = get_user_model()


@pytest.mark.django_db
class TestProjectAPI:

    def setup_method(self):
        self.client = APIClient()

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_list_projects(self):
        owner = User.objects.create_user(email="owner@test.com")
        self.authenticate(owner)

        Project.objects.create(owner=owner, name="Project 1")
        Project.objects.create(owner=owner, name="Project 2")

        response = self.client.get("/api/v1/projects/")

        assert response.status_code == 200
        assert "data" in response.data
        assert response.data["meta"]["total_items"] == 2

    def test_create_project(self):
        owner = User.objects.create_user(email="owner@test.com")
        self.authenticate(owner)

        response = self.client.post(
            "/api/v1/projects/",
            data={"name": "New Project", "description": "Desc"},
            format="json",
        )

        assert response.status_code == 201
        assert response.data["data"]["name"] == "New Project"

    def test_get_project_detail(self):
        owner = User.objects.create_user(email="owner@test.com")
        self.authenticate(owner)

        project = Project.objects.create(owner=owner, name="Project")

        response = self.client.get(f"/api/v1/projects/{project.id}/")

        assert response.status_code == 200
        assert response.data["data"]["id"] == str(project.id)

    def test_project_permission_denied(self):
        owner = User.objects.create_user(email="owner@test.com")
        other = User.objects.create_user(email="other@test.com")
        self.authenticate(other)

        project = Project.objects.create(owner=owner, name="Project")

        response = self.client.get(f"/api/v1/projects/{project.id}/")

        assert response.status_code == 403

    def test_delete_project(self):
        owner = User.objects.create_user(email="owner@test.com")
        self.authenticate(owner)

        project = Project.objects.create(owner=owner, name="Project")

        response = self.client.delete(f"/api/v1/projects/{project.id}/")

        assert response.status_code == 200

        project.refresh_from_db()
        assert project.is_active is False
