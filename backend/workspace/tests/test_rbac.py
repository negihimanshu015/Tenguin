import pytest
from django.contrib.auth import get_user_model
from project.models import Project
from rest_framework.test import APIClient
from workspace.models import Workspace, WorkspaceMember

User = get_user_model()

@pytest.mark.django_db
class TestRBAC:
    def setup_method(self):
        self.client = APIClient()

        # Create users
        self.owner_user = User.objects.create_user(email="owner@test.com", clerk_id="owner_1")
        self.admin_user = User.objects.create_user(email="admin@test.com", clerk_id="admin_1")
        self.member_user = User.objects.create_user(email="member@test.com", clerk_id="member_1")
        self.non_member = User.objects.create_user(email="non@test.com", clerk_id="non_1")

        # Create workspace and memberships
        self.workspace = Workspace.objects.create(owner=self.owner_user, name="RBAC Workspace")

        # Add admin
        WorkspaceMember.objects.create(
            workspace=self.workspace,
            user=self.admin_user,
            role=WorkspaceMember.Role.ADMIN
        )

        # Add member
        WorkspaceMember.objects.create(
            workspace=self.workspace,
            user=self.member_user,
            role=WorkspaceMember.Role.MEMBER
        )

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_workspace_deletion_rbac(self):
        # Admin cannot delete
        self.authenticate(self.admin_user)
        response = self.client.delete(f"/api/v1/workspaces/{self.workspace.id}/")
        assert response.status_code == 403

        # Member cannot delete
        self.authenticate(self.member_user)
        response = self.client.delete(f"/api/v1/workspaces/{self.workspace.id}/")
        assert response.status_code == 403

        # Owner CAN delete
        self.authenticate(self.owner_user)
        response = self.client.delete(f"/api/v1/workspaces/{self.workspace.id}/")
        assert response.status_code == 200

    def test_add_member_rbac(self):
        new_user = User.objects.create_user(email="new@test.com", clerk_id="new_1")

        # Member cannot add members
        self.authenticate(self.member_user)
        response = self.client.post(
            f"/api/v1/workspaces/{self.workspace.id}/members/manage/",
            data={"email": new_user.email}
        )
        assert response.status_code == 403

        # Admin CAN add members
        self.authenticate(self.admin_user)
        response = self.client.post(
            f"/api/v1/workspaces/{self.workspace.id}/members/manage/",
            data={"email": new_user.email}
        )
        assert response.status_code == 201

    def test_role_change_rbac(self):
        # Admin cannot change roles
        self.authenticate(self.admin_user)
        response = self.client.patch(
            f"/api/v1/workspaces/{self.workspace.id}/members/role/",
            data={"user_id": str(self.member_user.id), "role": WorkspaceMember.Role.ADMIN}
        )
        assert response.status_code == 403

        # Owner CAN change roles
        self.authenticate(self.owner_user)
        response = self.client.patch(
            f"/api/v1/workspaces/{self.workspace.id}/members/role/",
            data={"user_id": str(self.member_user.id), "role": WorkspaceMember.Role.ADMIN}
        )
        assert response.status_code == 200

        # Verify role changed
        membership = WorkspaceMember.objects.get(workspace=self.workspace, user=self.member_user)
        assert membership.role == WorkspaceMember.Role.ADMIN

    def test_project_management_rbac(self):
        # Member cannot create project
        self.authenticate(self.member_user)
        response = self.client.post(
            "/api/v1/projects/",
            data={"workspace_id": str(self.workspace.id), "name": "Member Project"}
        )
        assert response.status_code == 403

        # Admin CAN create project
        self.authenticate(self.admin_user)
        response = self.client.post(
            "/api/v1/projects/",
            data={"workspace_id": str(self.workspace.id), "name": "Admin Project"}
        )
        assert response.status_code == 201
        project_id = response.data["data"]["id"]

        # Member CAN view project (member of workspace)
        self.authenticate(self.member_user)
        response = self.client.get(f"/api/v1/projects/{project_id}/")
        assert response.status_code == 200

    def test_task_management_rbac(self):
        # Setup: Admin creates a project
        project = Project.objects.create(workspace=self.workspace, name="Internal Project")

        # Member CAN create task
        self.authenticate(self.member_user)
        response = self.client.post(
            f"/api/v1/projects/{project.id}/tasks/",
            data={"title": "Member Task"}
        )
        assert response.status_code == 201
        task_id = response.data["data"]["id"]

        # Non-member cannot view task
        self.authenticate(self.non_member)
        response = self.client.get(f"/api/v1/projects/{project.id}/tasks/{task_id}/")
        assert response.status_code == 403
