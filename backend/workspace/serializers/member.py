from rest_framework import serializers


class UserSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()

class WorkspaceMemberSerializer(serializers.Serializer):
    user = UserSerializer()
    role = serializers.CharField()
    joined_at = serializers.DateTimeField(source="created")
