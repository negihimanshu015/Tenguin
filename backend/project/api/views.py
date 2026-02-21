from core.exceptions import NotFoundException
from core.pagination import DefaultPagination
from core.response import (
    created,
    deleted,
    success,
    updated,
)
from project.permissions import IsProjectOwner
from project.selectors import (
    get_active_project,
    get_active_project_by_id,
)
from project.serializers.project_detail import ProjectDetailSerializer
from project.serializers.project_list import ProjectListSerializer
from project.serializers.project_write import ProjectWriteSerializer
from project.services import ProjectService
from rest_framework.views import APIView


class ProjectListCreateView(APIView):

    def get(self, request):
        queryset = get_active_project(owner=request.user)

        paginator = DefaultPagination()
        page = paginator.paginate_queryset(queryset, request)

        serializer = ProjectListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = ProjectWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        project = ProjectService.create_project(
            owner=request.user,
            name=serializer.validated_data["name"],
            description=serializer.validated_data.get("description", ""),
        )

        return created(
            data=ProjectDetailSerializer(project).data
        )


class ProjectDetailView(APIView):
    permission_classes = [IsProjectOwner]

    def get_object(self):
        project = get_active_project_by_id(
            owner=self.request.user,
            project_id=self.kwargs["project_id"],
        )
        if project is None:
            return None
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
            owner=request.user,
            project_id=project_id,
            name=serializer.validated_data["name"],
            description=serializer.validated_data.get("description", ""),
        )

        return updated(
            data=ProjectDetailSerializer(project).data
        )

    def delete(self, request, project_id):
        ProjectService.delete_project(
            owner=request.user,
            project_id=project_id,
        )
        return deleted()
