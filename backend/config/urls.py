from core.views.auth_test import AuthDebugView
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/test/", AuthDebugView.as_view()),

    path("api/health/", include("health.urls")),

    path("api/v1/projects/", include("project.urls")),
    path("api/v1/", include("tasks.urls")),
]
