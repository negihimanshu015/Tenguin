from django.contrib import admin
from django.urls import include, path
from core.views.auth_test import AuthDebugView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/test/", AuthDebugView.as_view()),

    path("api/v1/projects/", include("project.urls")),
    path("api/v1/", include("tasks.urls")),
]
