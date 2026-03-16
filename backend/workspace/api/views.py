from core.pagination import DefaultPagination
from core.response import (
    created,
    deleted,
    success,
    updated,
)
from rest_framework.views import APIView
from workspace.permissions import IsWorkspaceOwner
from workspace.selectors import (
    get_active_workspaces,
    get_workspace_members,
)
from workspace.serializers.member import WorkspaceMemberSerializer
from workspace.serializers.workspace_detail import WorkspaceDetailSerializer
from workspace.serializers.workspace_list import WorkspaceListSerializer
from workspace.serializers.workspace_write import WorkspaceWriteSerializer
from workspace.services import WorkspaceService


class WorkspaceListCreateView(APIView):

    def get(self, request):
        queryset = get_active_workspaces(
            owner=request.user,
        )

        paginator = DefaultPagination()
        page = paginator.paginate_queryset(queryset, request)

        serializer = WorkspaceListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = WorkspaceWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        workspace = WorkspaceService.create_workspace(
            owner=request.user,
            name=serializer.validated_data["name"],
            description=serializer.validated_data.get("description", ""),
        )

        return created(
            data=WorkspaceDetailSerializer(workspace).data
        )


class WorkspaceDetailView(APIView):
    permission_classes = [IsWorkspaceOwner]

    def get(self, request, workspace_id):
        workspace = WorkspaceService.get_workspace_for_owner(
            owner=request.user,
            workspace_id=workspace_id,
        )
        return success(
            data=WorkspaceDetailSerializer(workspace).data
        )

    def put(self, request, workspace_id):
        serializer = WorkspaceWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        workspace = WorkspaceService.update_workspace(
            owner=request.user,
            workspace_id=workspace_id,
            name=serializer.validated_data.get("name"),
            description=serializer.validated_data.get("description"),
        )

        return updated(
            data=WorkspaceDetailSerializer(workspace).data
        )

    def delete(self, request, workspace_id):
        WorkspaceService.delete_workspace(
            owner=request.user,
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
    permission_classes = [IsWorkspaceOwner]

    def post(self, request, workspace_id):
        email = request.data.get("email")
        if not email:
            from core.exceptions import ValidationException
            raise ValidationException("Email is required")

        WorkspaceService.add_member(
            owner=request.user,
            workspace_id=workspace_id,
            email=email,
        )
        return success(
            data={"message": f"User {email} added successfully"},
            status=201
        )

    def delete(self, request, workspace_id):
        user_id = request.data.get("user_id")
        if not user_id:
            from core.exceptions import ValidationException
            raise ValidationException("User ID is required")

        WorkspaceService.remove_member(
            owner=request.user,
            workspace_id=workspace_id,
            user_id=user_id,
        )
        return deleted()
