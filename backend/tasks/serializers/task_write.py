from django.utils import timezone
from rest_framework import serializers
from tasks.models import Task


class TaskWriteSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(allow_blank=True, required=False)
    assignee = serializers.UUIDField(required=False, allow_null=True)
    status = serializers.ChoiceField(choices=Task.Status.choices, required=False)
    priority = serializers.ChoiceField(choices=Task.Priority.choices, required=False)
    due_date = serializers.DateField(required=False, allow_null=True)
    ordering = serializers.IntegerField(required=False)

    def validate_due_date(self, value):
        if value and value < timezone.now().date():
            raise serializers.ValidationError("Due date cannot be in the past.")
        return value
