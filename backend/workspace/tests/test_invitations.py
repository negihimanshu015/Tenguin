import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from workspace.models import Workspace, WorkspaceInvitation, WorkspaceMember

User = get_user_model()

@pytest.mark.django_db
class TestWorkspaceInvitations:
    def setup_method(self):
        self.client = APIClient()

        # Create users
        self.owner = User.objects.create_user(email="owner@test.com", clerk_id="owner_1")
        self.admin = User.objects.create_user(email="admin@test.com", clerk_id="admin_1")
        self.member = User.objects.create_user(email="member@test.com", clerk_id="member_1")
        self.invitee = User.objects.create_user(email="invitee@test.com", clerk_id="invitee_1")

        # Create workspace
        self.workspace = Workspace.objects.create(owner=self.owner, name="Test Workspace")

        # Add admin
        WorkspaceMember.objects.create(
            workspace=self.workspace,
            user=self.admin,
            role=WorkspaceMember.Role.ADMIN
        )

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_create_invitation_rbac(self):
        # Member cannot create invitation
        self.authenticate(self.member)
        response = self.client.post(
            f"/api/v1/workspaces/{self.workspace.id}/invitations/",
            data={"email": "new@test.com", "role": "MEMBER"}
        )
        assert response.status_code == 403

        # Admin CAN create invitation
        self.authenticate(self.admin)
        response = self.client.post(
            f"/api/v1/workspaces/{self.workspace.id}/invitations/",
            data={"email": "new@test.com", "role": "MEMBER"}
        )
        assert response.status_code == 201
        assert WorkspaceInvitation.objects.filter(email="new@test.com").exists()

    def test_accept_invitation_flow(self):
        # 1. Create invitation
        self.authenticate(self.admin)
        response = self.client.post(
            f"/api/v1/workspaces/{self.workspace.id}/invitations/",
            data={"email": self.invitee.email, "role": "MEMBER"}
        )
        token = response.data["data"]["token"]

        # 2. Accept invitation
        self.authenticate(self.invitee)
        response = self.client.post(
            "/api/v1/workspaces/invitations/accept/",
            data={"token": token}
        )
        assert response.status_code == 200

        # 3. Verify membership
        assert WorkspaceMember.objects.filter(
            workspace=self.workspace,
            user=self.invitee,
            role=WorkspaceMember.Role.MEMBER,
            is_active=True
        ).exists()

        # 4. Verify invitation status
        invitation = WorkspaceInvitation.objects.get(token=token)
        assert invitation.status == WorkspaceInvitation.Status.ACCEPTED

    def test_expired_invitation(self):
        # 1. Create an expired invitation manually
        invitation = WorkspaceInvitation.objects.create(
            workspace=self.workspace,
            email=self.invitee.email,
            invited_by=self.owner,
            expires_at=timezone.now() - timezone.timedelta(days=1),
            status=WorkspaceInvitation.Status.PENDING
        )

        # 2. Try to accept
        self.authenticate(self.invitee)
        response = self.client.post(
            "/api/v1/workspaces/invitations/accept/",
            data={"token": str(invitation.token)}
        )
        assert response.status_code == 400
        assert "expired" in response.data["message"].lower()

    def test_revoke_invitation(self):
        # 1. Create invitation
        invitation = WorkspaceInvitation.objects.create(
            workspace=self.workspace,
            email="to_revoke@test.com",
            invited_by=self.owner,
            expires_at=timezone.now() + timezone.timedelta(days=7),
            status=WorkspaceInvitation.Status.PENDING
        )

        # 2. Revoke invitation
        self.authenticate(self.admin)
        response = self.client.delete(
            f"/api/v1/workspaces/{self.workspace.id}/invitations/{invitation.id}/"
        )
        assert response.status_code == 200

        invitation.refresh_from_db()
        assert invitation.status == WorkspaceInvitation.Status.REVOKED

    def test_unique_pending_invitation(self):
        # 1. Create invitation
        self.authenticate(self.admin)
        self.client.post(
            f"/api/v1/workspaces/{self.workspace.id}/invitations/",
            data={"email": "unique@test.com", "role": "MEMBER"}
        )

        # 2. Try to create again for same email/workspace
        response = self.client.post(
            f"/api/v1/workspaces/{self.workspace.id}/invitations/",
            data={"email": "unique@test.com", "role": "MEMBER"}
        )
        assert response.status_code == 409
        assert "already exists" in response.data["message"].lower()

    def test_workspace_deletion_revokes_invitations(self):
        # 1. Create invitation
        invitation = WorkspaceInvitation.objects.create(
            workspace=self.workspace,
            email="revokeme@test.com",
            invited_by=self.owner,
            expires_at=timezone.now() + timezone.timedelta(days=7),
            status=WorkspaceInvitation.Status.PENDING
        )

        # 2. Delete workspace (as owner)
        from workspace.services import WorkspaceService
        WorkspaceService.delete_workspace(user=self.owner, workspace_id=self.workspace.id)

        # 3. Verify invitation is revoked
        invitation.refresh_from_db()
        assert invitation.status == WorkspaceInvitation.Status.REVOKED

    def test_get_my_invitations(self):
        # 1. Create invitations for 'invitee'
        WorkspaceInvitation.objects.create(
            workspace=self.workspace,
            email=self.invitee.email,
            invited_by=self.owner,
            expires_at=timezone.now() + timezone.timedelta(days=7),
            status=WorkspaceInvitation.Status.PENDING
        )

        # 2. Fetch 'me' invitations
        self.authenticate(self.invitee)
        response = self.client.get("/api/v1/workspaces/invitations/me/")
        assert response.status_code == 200
        assert len(response.data["data"]) == 1
        assert response.data["data"][0]["workspace_name"] == self.workspace.name
