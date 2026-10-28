"""
Festora API URL Configuration
"""

from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health_check(request):
    return JsonResponse(
        {
            "status": "ok",
            "service": "festora-api",
            "version": "1.0.0",
            "tagline": "GenAI-Powered Celebration & Event Planner",
        }
    )


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_check, name="health_check"),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/events/", include("apps.events.urls")),
    path("api/guests/", include("apps.guests.urls")),
    path("api/budget/", include("apps.budget.urls")),
    path("api/tasks/", include("apps.tasks.urls")),
    path("api/vendors/", include("apps.vendors.urls")),
    path("api/ai/", include("apps.ai.urls")),
    path("api/notifications/", include("apps.notifications.urls")),
]
