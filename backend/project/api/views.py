from core.exceptions import NotFoundException
from core.pagination import DefaultPagination
from core.response import (
    created,
    deleted,
    success,
    updated,
)
from project.permissions import IsProjectWorkspaceAdmin
from project.selectors import (
    get_active_project,
)
from project.serializers.project_detail import ProjectDetailSerializer
from project.serializers.project_list import ProjectListSerializer
from project.serializers.project_write import ProjectWriteSerializer
from project.services import ProjectService
from rest_framework.views import APIView


class ProjectListCreateView(APIView):

    def get(self, request):
        workspace_id = request.query_params.get("workspace_id")
        queryset = get_active_project(user=request.user, workspace_id=workspace_id)

        paginator = DefaultPagination()
        page = paginator.paginate_queryset(queryset, request)

        serializer = ProjectListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = ProjectWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        project = ProjectService.create_project(
            user=request.user,
            workspace_id=serializer.validated_data["workspace_id"],
            name=serializer.validated_data["name"],
            description=serializer.validated_data.get("description", ""),
        )

        return created(
            data=ProjectDetailSerializer(project).data
        )


class ProjectDetailView(APIView):
    permission_classes = [IsProjectWorkspaceAdmin]

    def get_permissions(self):
        if self.request.method == "GET":
            from workspace.permissions import IsWorkspaceMember
            return [IsWorkspaceMember()]
        return super().get_permissions()

    def get_object(self):
        # We use a custom fetch here instead of selector to ensure role check
        project_id = self.kwargs["project_id"]
        from project.services import ProjectService
        project = ProjectService.get_project_for_user(
            user=self.request.user,
            project_id=project_id,
        )
        self.check_object_permissions(self.request, project)
        return project

    def get(self, request, project_id):
        project = self.get_object()
        if project is None:
            raise NotFoundException("Project not found")

        return success(
            data=ProjectDetailSerializer(project).data
        )

    def put(self, request, project_id):
        serializer = ProjectWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        project = ProjectService.update_project(
            user=request.user,
            project_id=project_id,
            name=serializer.validated_data["name"],
            description=serializer.validated_data.get("description", ""),
        )

        return updated(
            data=ProjectDetailSerializer(project).data
        )

    def delete(self, request, project_id):
        ProjectService.delete_project(
            user=request.user,
            project_id=project_id,
        )
        return deleted()
class ProjectTrashListView(APIView):
    def get(self, request):
        workspace_id = request.query_params.get("workspace_id")
        if not workspace_id:
            from core.exceptions import ValidationException
            raise ValidationException("workspace_id is required")

        from project.selectors import get_deleted_projects
        queryset = get_deleted_projects(user=request.user, workspace_id=workspace_id)

        paginator = DefaultPagination()
        page = paginator.paginate_queryset(queryset, request)

        serializer = ProjectListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class ProjectRestoreView(APIView):
    def post(self, request, project_id):
        project = ProjectService.restore_project(
            user=request.user,
            project_id=project_id,
        )
        return success(
            data=ProjectDetailSerializer(project).data,
            message="Project restored successfully"
        )


class ProjectPermanentDeleteView(APIView):
    def delete(self, request, project_id):
        ProjectService.permanent_delete_project(
            user=request.user,
            project_id=project_id,
        )
        return success(message="Project permanently deleted")
