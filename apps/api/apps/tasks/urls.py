from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ScheduleConflictsView, ScheduleItemViewSet, TaskViewSet

router = DefaultRouter()
router.register("items", TaskViewSet, basename="tasks")
router.register("schedule", ScheduleItemViewSet, basename="schedule")

urlpatterns = [
    path(
        "conflicts/<uuid:event_id>/",
        ScheduleConflictsView.as_view(),
        name="schedule_conflicts",
    ),
    path("", include(router.urls)),
]
