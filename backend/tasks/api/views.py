from core.pagination import DefaultPagination
from core.response import (
    created,
    deleted,
    success,
    updated,
)
from rest_framework.views import APIView
from tasks.permissions import (
    IsTaskProjectMember,
)
from tasks.selectors import (
    get_active_tasks,
    get_active_tasks_assigned_to_user,
)
from tasks.serializers.task_detail import TaskDetailSerializer
from tasks.serializers.task_list import TaskListSerializer
from tasks.serializers.task_write import TaskWriteSerializer
from tasks.services import TaskService


class TaskListCreateView(APIView):

    def get(self, request, project_id):
        queryset = get_active_tasks(
            user=request.user,
            project_id=project_id,
        )

        paginator = DefaultPagination()
        page = paginator.paginate_queryset(queryset, request)

        serializer = TaskListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, project_id):
        serializer = TaskWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        task = TaskService.create_task(
            user=request.user,
            project_id=project_id,
            title=serializer.validated_data["title"],
            description=serializer.validated_data.get("description", ""),
            assignee_id=serializer.validated_data.get("assignee"),
            status=serializer.validated_data.get("status"),
            priority=serializer.validated_data.get("priority"),
            due_date=serializer.validated_data.get("due_date"),
            ordering=serializer.validated_data.get("ordering", 0),
        )

        return created(
            data=TaskDetailSerializer(task).data
        )


class TaskDetailView(APIView):
    permission_classes = [IsTaskProjectMember]

    def get(self, request, project_id, task_id):
        task = TaskService.get_task_for_user(
            user=request.user,
            task_id=task_id,
        )
        return success(
            data=TaskDetailSerializer(task).data
        )

    def put(self, request, project_id, task_id):
        serializer = TaskWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        task = TaskService.update_task(
            user=request.user,
            task_id=task_id,
            title=serializer.validated_data.get("title"),
            description=serializer.validated_data.get("description"),
            assignee_id=serializer.validated_data.get("assignee"),
            status=serializer.validated_data.get("status"),
            priority=serializer.validated_data.get("priority"),
            due_date=serializer.validated_data.get("due_date"),
            ordering=serializer.validated_data.get("ordering"),
        )

        return updated(
            data=TaskDetailSerializer(task).data
        )

    def delete(self, request, project_id, task_id):
        TaskService.delete_task(
            user=request.user,
            task_id=task_id,
        )
        return deleted()


class AssignedTaskListView(APIView):

    def get(self, request):
        queryset = get_active_tasks_assigned_to_user(
            assignee=request.user,
        )

        paginator = DefaultPagination()
        page = paginator.paginate_queryset(queryset, request)

        serializer = TaskListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
