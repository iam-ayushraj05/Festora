from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Task, ScheduleItem
from .serializers import TaskSerializer, ScheduleItemSerializer
from .services import find_schedule_conflicts
from apps.events.models import Event
from apps.events.permissions import IsEventMember

class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsEventMember]
    serializer_class = TaskSerializer

    def get_queryset(self):
        event_id = self.request.query_params.get('event')
        queryset = Task.objects.filter(event__members__user=self.request.user)
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        return queryset.distinct()

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        task = self.get_object()
        task.mark_completed()
        return Response(TaskSerializer(task).data)

class ScheduleItemViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsEventMember]
    serializer_class = ScheduleItemSerializer

    def get_queryset(self):
        event_id = self.request.query_params.get('event')
        queryset = ScheduleItem.objects.filter(event__members__user=self.request.user)
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        return queryset.distinct()

class ScheduleConflictsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, event_id):
        event = Event.objects.filter(id=event_id, members__user=request.user).first()
        if not event:
            return Response({'error': 'Event not found or unauthorized'}, status=status.HTTP_404_NOT_FOUND)
        conflicts = find_schedule_conflicts(event)
        return Response({'conflicts': conflicts, 'conflict_count': len(conflicts)})
