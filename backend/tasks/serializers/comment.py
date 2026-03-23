from core.serializers.user import UserSerializer
from rest_framework import serializers
from tasks.models import Comment


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "task",
            "author",
            "content",
            "created",
            "updated",
        ]
        read_only_fields = ["id", "task", "author", "created", "updated"]
