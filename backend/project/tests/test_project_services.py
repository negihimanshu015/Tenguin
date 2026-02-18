import pytest

from django.contrib.auth import get_user_model

from project.models import Project
from project.services import ProjectService
from core.exceptions import (
    NotFoundException,
    PermissionException,
    ConflictException,
)

User = get_user_model()


@pytest.mark.django_db
class TestProjectService:

    def test_create_project(self):
        owner = User.objects.create_user(email="owner@test.com", clerk_id="user_123")

        project = ProjectService.create_project(
            owner=owner,
            name="My Project",
            description="Test description",
        )

        assert project.owner == owner
        assert project.name == "My Project"
        assert project.description == "Test description"

    def test_create_project_name_unique_per_owner(self):
        owner = User.objects.create_user(email="owner@test.com", clerk_id="user_123")

        ProjectService.create_project(
            owner=owner,
            name="My Project",
            description="",
        )

        with pytest.raises(ConflictException):
            ProjectService.create_project(
                owner=owner,
                name="My Project",
                description="",
            )

    def test_get_project_for_owner_success(self):
        owner = User.objects.create_user(email="owner@test.com", clerk_id="user_123")
        project = Project.objects.create(owner=owner, name="Project")

        result = ProjectService.get_project_for_owner(
            owner=owner,
            project_id=project.id,
        )

        assert result == project

    def test_get_project_for_owner_not_found(self):
        owner = User.objects.create_user(email="owner@test.com", clerk_id="user_123")

        with pytest.raises(PermissionException):
            ProjectService.get_project_for_owner(
                owner=owner,
                project_id="00000000-0000-0000-0000-000000000000",
            )

    def test_get_project_for_owner_permission_denied(self):
        owner = User.objects.create_user(email="owner@test.com", clerk_id="user_123")
        other = User.objects.create_user(email="other@test.com", clerk_id="user_456")

        project = Project.objects.create(owner=other, name="Project")

        with pytest.raises(PermissionException):
            ProjectService.get_project_for_owner(
                owner=owner,
                project_id=project.id,
            )

    def test_update_project(self):
        owner = User.objects.create_user(email="owner@test.com", clerk_id="user_123")
        project = Project.objects.create(owner=owner, name="Old Name")

        updated = ProjectService.update_project(
            owner=owner,
            project_id=project.id,
            name="New Name",
            description="Updated",
        )

        assert updated.name == "New Name"
        assert updated.description == "Updated"

    def test_delete_project_soft_delete(self):
        owner = User.objects.create_user(email="owner@test.com", clerk_id="user_123")
        project = Project.objects.create(owner=owner, name="Project")

        ProjectService.delete_project(
            owner=owner,
            project_id=project.id,
        )

        project.refresh_from_db()
        assert project.is_active is False
