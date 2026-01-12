from rest_framework import serializers


class TaskWriteSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(allow_blank=True, required=False)
    assignee = serializers.UUIDField(required=False, allow_null=True)
    is_completed = serializers.BooleanField(required=False)
