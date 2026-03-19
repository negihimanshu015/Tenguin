from core.pagination import DefaultPagination
from core.response import (
    created,
    deleted,
    success,
    updated,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from workspace.permissions import (
    IsWorkspaceAdmin,
    IsWorkspaceMember,
    IsWorkspaceOwner,
)
from workspace.selectors import (
    get_active_workspaces,
    get_workspace_members,
)
from workspace.serializers.invitation import (
    WorkspaceInvitationAcceptSerializer,
    WorkspaceInvitationCreateSerializer,
    WorkspaceInvitationSerializer,
)
from workspace.serializers.member import WorkspaceMemberSerializer
from workspace.serializers.workspace_detail import WorkspaceDetailSerializer
from workspace.serializers.workspace_list import WorkspaceListSerializer
from workspace.serializers.workspace_write import WorkspaceWriteSerializer
from workspace.services import WorkspaceService


class WorkspaceListCreateView(APIView):

    def get(self, request):
        queryset = get_active_workspaces(
            user=request.user,
        )

        paginator = DefaultPagination()
        page = paginator.paginate_queryset(queryset, request)

        serializer = WorkspaceListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = WorkspaceWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        workspace = WorkspaceService.create_workspace(
            user=request.user,
            name=serializer.validated_data["name"],
            description=serializer.validated_data.get("description", ""),
        )

        return created(
            data=WorkspaceDetailSerializer(workspace).data
        )


class WorkspaceDetailView(APIView):
    permission_classes = [IsWorkspaceMember]

    def get(self, request, workspace_id):
        workspace = WorkspaceService.get_workspace_for_user_with_role(
            user=request.user,
            workspace_id=workspace_id,
        )
        return success(
            data=WorkspaceDetailSerializer(workspace).data
        )

    def put(self, request, workspace_id):
        serializer = WorkspaceWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        workspace = WorkspaceService.update_workspace(
            user=request.user,
            workspace_id=workspace_id,
            name=serializer.validated_data.get("name"),
            description=serializer.validated_data.get("description"),
        )

        return updated(
            data=WorkspaceDetailSerializer(workspace).data
        )

    def delete(self, request, workspace_id):
        WorkspaceService.delete_workspace(
            user=request.user,
            workspace_id=workspace_id,
        )
        return deleted()


class WorkspaceMemberListView(APIView):

    def get(self, request, workspace_id):
        members = get_workspace_members(
            user=request.user,
            workspace_id=workspace_id,
        )
        serializer = WorkspaceMemberSerializer(members, many=True)
        return success(data=serializer.data)


class WorkspaceMemberAddRemoveView(APIView):
    permission_classes = [IsWorkspaceAdmin]

    def post(self, request, workspace_id):
        email = request.data.get("email")
        if not email:
            from core.exceptions import ValidationException
            raise ValidationException("Email is required")

        WorkspaceService.add_member(
            user=request.user,
            workspace_id=workspace_id,
            email=email,
        )
        return created(
            data={"message": f"User {email} added successfully"}
        )

    def delete(self, request, workspace_id):
        user_id = request.data.get("user_id")
        if not user_id:
            from core.exceptions import ValidationException
            raise ValidationException("User ID is required")

        WorkspaceService.remove_member(
            user=request.user,
            workspace_id=workspace_id,
            user_id=user_id,
        )
        return deleted()

class WorkspaceMemberRoleChangeView(APIView):
    permission_classes = [IsWorkspaceOwner]

    def patch(self, request, workspace_id):
        user_id = request.data.get("user_id")
        role = request.data.get("role")
        if not user_id or not role:
            from core.exceptions import ValidationException
            raise ValidationException("User ID and Role are required")

        WorkspaceService.change_member_role(
            user=request.user,
            workspace_id=workspace_id,
            user_id=user_id,
            role=role,
        )
        return success(data={"message": "Role updated successfully"})


class WorkspaceInvitationListCreateView(APIView):
    permission_classes = [IsWorkspaceAdmin]

    def get(self, request, workspace_id):
        from workspace.models import WorkspaceInvitation
        invitations = WorkspaceInvitation.objects.filter(
            workspace_id=workspace_id,
            status=WorkspaceInvitation.Status.PENDING
        ).order_by("-created")

        serializer = WorkspaceInvitationSerializer(invitations, many=True)
        return success(data=serializer.data)

    def post(self, request, workspace_id):
        serializer = WorkspaceInvitationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        invitation = WorkspaceService.invite_member(
            user=request.user,
            workspace_id=workspace_id,
            email=serializer.validated_data["email"],
            role=serializer.validated_data.get("role", "MEMBER"),
        )

        return created(
            data=WorkspaceInvitationSerializer(invitation).data
        )


class WorkspaceInvitationRevokeView(APIView):
    permission_classes = [IsWorkspaceAdmin]

    def delete(self, request, workspace_id, invitation_id):
        WorkspaceService.revoke_invitation(
            user=request.user,
            invitation_id=invitation_id,
        )
        return deleted()


class WorkspaceInvitationAcceptView(APIView):
    # This endpoint is designed to be public (or at least accessible with a token)
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = WorkspaceInvitationAcceptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        WorkspaceService.accept_invitation(
            user=request.user,
            token=serializer.validated_data["token"],
        )
        return success(message="Invitation accepted successfully")


class WorkspaceInvitationMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        invitations = WorkspaceService.get_invitations_for_user(
            email=request.user.email
        )
        serializer = WorkspaceInvitationSerializer(invitations, many=True)
        return success(data=serializer.data)
