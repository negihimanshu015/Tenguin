import pytest

from django.contrib.auth import get_user_model

from project.models import Project
from project.selectors import (
    get_active_project,
    get_active_project_by_id,
)

User = get_user_model()


@pytest.mark.django_db
class TestProjectSelectors:

    def test_get_active_projects_for_owner_returns_only_owner_projects(self):
        owner = User.objects.create_user(email="owner@test.com", clerk_id="user_123")
        other = User.objects.create_user(email="other@test.com", clerk_id="user_456")

        Project.objects.create(owner=owner, name="Owner Project")
        Project.objects.create(owner=other, name="Other Project")

        projects = get_active_project(owner=owner)

        assert projects.count() == 1
        assert projects.first().owner == owner

    def test_get_active_projects_excludes_soft_deleted(self):
        owner = User.objects.create_user(email="owner@test.com", clerk_id="user_123")

        project = Project.objects.create(owner=owner, name="Active Project")
        deleted_project = Project.objects.create(owner=owner, name="Deleted Project")
        deleted_project.soft_delete()

        projects = get_active_project(owner=owner)

        assert project in projects
        assert deleted_project not in projects

    def test_get_active_project_by_id_returns_project_for_owner(self):
        owner = User.objects.create_user(email="owner@test.com", clerk_id="user_123")

        project = Project.objects.create(owner=owner, name="Project")

        result = get_active_project_by_id(
            owner=owner,
            project_id=project.id,
        )

        assert result == project

    def test_get_active_project_by_id_returns_none_for_other_owner(self):
        owner = User.objects.create_user(email="owner@test.com", clerk_id="user_123")
        other = User.objects.create_user(email="other@test.com", clerk_id="user_456")

        project = Project.objects.create(owner=other, name="Project")

        result = get_active_project_by_id(
            owner=owner,
            project_id=project.id,
        )

        assert result is None

    def test_get_active_project_by_id_returns_none_if_soft_deleted(self):
        owner = User.objects.create_user(email="owner@test.com", clerk_id="user_123")

        project = Project.objects.create(owner=owner, name="Project")
        project.soft_delete()

        result = get_active_project_by_id(
            owner=owner,
            project_id=project.id,
        )

        assert result is None
