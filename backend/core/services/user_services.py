from django.contrib.auth import get_user_model
from django.db import transaction
from workspace.services import WorkspaceService


def create_user(*, clerk_id: str, payload: dict):
    User = get_user_model()
    defaults = {
        "clerk_id": clerk_id,
        "email": payload.get("email") or f"{clerk_id}@clerk.local",
        "first_name": payload.get("first_name", ""),
        "last_name": payload.get("last_name", ""),
    }

    with transaction.atomic():
        user = User.objects.create(**defaults)
        WorkspaceService.create_personal_workspace(user=user)
        return user
