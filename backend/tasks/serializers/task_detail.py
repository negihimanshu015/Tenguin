from rest_framework import serializers


class TaskDetailSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    title = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    is_completed = serializers.BooleanField(read_only=True)
    assignee = serializers.UUIDField(source="assignee_id", read_only=True)
    project_id = serializers.UUIDField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
