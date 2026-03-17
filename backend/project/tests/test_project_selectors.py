import pytest
from django.contrib.auth import get_user_model
from project.models import Project
from project.selectors import (
    get_active_project,
    get_active_project_by_id,
)
from workspace.models import Workspace

User = get_user_model()


@pytest.mark.django_db
class TestProjectSelectors:

    def test_get_active_projects_for_owner_returns_only_owner_projects(self):
        owner = User.objects.create_user(email="owner@test.com", clerk_id="user_123")
        other = User.objects.create_user(email="other@test.com", clerk_id="user_456")

        ws_owner = Workspace.objects.create(owner=owner, name="Owner WS")
        ws_other = Workspace.objects.create(owner=other, name="Other WS")

        Project.objects.create(workspace=ws_owner, name="Owner Project")
        Project.objects.create(workspace=ws_other, name="Other Project")

        projects = get_active_project(user=owner)

        assert projects.count() == 1
        assert projects.first().workspace.owner == owner

    def test_get_active_projects_excludes_soft_deleted(self):
        owner = User.objects.create_user(email="owner@test.com", clerk_id="user_123")
        ws = Workspace.objects.create(owner=owner, name="WS")

        project = Project.objects.create(workspace=ws, name="Active Project")
        deleted_project = Project.objects.create(workspace=ws, name="Deleted Project")
        deleted_project.soft_delete()

        projects = get_active_project(user=owner)

        assert project in projects
        assert deleted_project not in projects

    def test_get_active_project_by_id_returns_project_for_owner(self):
        owner = User.objects.create_user(email="owner@test.com", clerk_id="user_123")
        ws = Workspace.objects.create(owner=owner, name="WS")

        project = Project.objects.create(workspace=ws, name="Project")

        result = get_active_project_by_id(
            user=owner,
            project_id=project.id,
        )

        assert result == project

    def test_get_active_project_by_id_returns_none_for_other_owner(self):
        owner = User.objects.create_user(email="owner@test.com", clerk_id="user_123")
        other = User.objects.create_user(email="other@test.com", clerk_id="user_456")

        ws_other = Workspace.objects.create(owner=other, name="Other WS")

        project = Project.objects.create(workspace=ws_other, name="Project")

        result = get_active_project_by_id(
            user=owner,
            project_id=project.id,
        )

        assert result is None

    def test_get_active_project_by_id_returns_none_if_soft_deleted(self):
        owner = User.objects.create_user(email="owner@test.com", clerk_id="user_123")
        ws = Workspace.objects.create(owner=owner, name="WS")

        project = Project.objects.create(workspace=ws, name="Project")
        project.soft_delete()

        result = get_active_project_by_id(
            user=owner,
            project_id=project.id,
        )

        assert result is None

