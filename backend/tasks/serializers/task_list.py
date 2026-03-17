from rest_framework import serializers


class TaskListSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    title = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    status = serializers.IntegerField(read_only=True)
    priority = serializers.IntegerField(read_only=True)
    due_date = serializers.DateField(read_only=True)
    ordering = serializers.IntegerField(read_only=True)
    assignee = serializers.UUIDField(source="assignee_id", read_only=True)
    project_id = serializers.UUIDField(read_only=True)
    project_name = serializers.CharField(source="project.name", read_only=True)
