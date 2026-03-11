from core.views.auth_test import AuthDebugView
from core.views.user import MeView
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/test/", AuthDebugView.as_view()),

    path("api/health/", include("health.urls")),

    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema")),

    path("api/v1/workspaces/", include("workspace.urls")),
    path("api/v1/projects/", include("project.urls")),
    path("api/v1/users/me/", MeView.as_view(), name="me"),
    path("api/v1/", include("tasks.urls")),
]
