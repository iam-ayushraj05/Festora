from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, ScheduleItemViewSet, ScheduleConflictsView

router = DefaultRouter()
router.register('items', TaskViewSet, basename='tasks')
router.register('schedule', ScheduleItemViewSet, basename='schedule')

urlpatterns = [
    path('conflicts/<uuid:event_id>/', ScheduleConflictsView.as_view(), name='schedule_conflicts'),
    path('', include(router.urls)),
]
