from core.serializers.user import UserSerializer
from rest_framework import serializers
from workspace.models import WorkspaceInvitation


class WorkspaceInvitationSerializer(serializers.ModelSerializer):
    invited_by = UserSerializer(read_only=True)
    workspace_name = serializers.CharField(source="workspace.name", read_only=True)

    class Meta:
        model = WorkspaceInvitation
        fields = (
            "id",
            "workspace",
            "workspace_name",
            "email",
            "role",
            "invited_by",
            "token",
            "status",
            "expires_at",
            "created",
            "updated",
        )
        read_only_fields = ("id", "token", "status", "invited_by", "created", "updated", "workspace_name")

class WorkspaceInvitationCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.CharField(required=False)

class WorkspaceInvitationAcceptSerializer(serializers.Serializer):
    token = serializers.UUIDField()
