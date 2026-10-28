import pytest
from datetime import timedelta
from django.utils import timezone
from apps.events.models import Event
from apps.tasks.models import Task, TaskPriority, TaskStatus, ScheduleItem
from apps.tasks.services import find_schedule_conflicts

@pytest.mark.django_db
class TestTasksAndTimeline:
    def test_task_completion_lifecycle(self):
        event = Event.objects.create(name="Festora Tasks Event")
        task = Task.objects.create(
            event=event,
            title="Book florists",
            priority=TaskPriority.HIGH,
            status=TaskStatus.TODO
        )
        assert task.completed_at is None
        task.mark_completed()
        assert task.status == TaskStatus.COMPLETED
        assert task.completed_at is not None

    def test_schedule_overlap_conflict_detection(self):
        event = Event.objects.create(name="Festora Run of Show")
        base_time = timezone.now().replace(minute=0, second=0, microsecond=0)

        # Item A: 10:00 - 12:00
        item_a = ScheduleItem.objects.create(
            event=event,
            title="Ceremony Setup",
            start_time=base_time,
            end_time=base_time + timedelta(hours=2)
        )

        # Item B: 11:00 - 13:00 (Overlaps with A!)
        item_b = ScheduleItem.objects.create(
            event=event,
            title="Band Soundcheck",
            start_time=base_time + timedelta(hours=1),
            end_time=base_time + timedelta(hours=3)
        )

        # Item C: 14:00 - 15:00 (No overlap)
        ScheduleItem.objects.create(
            event=event,
            title="Reception Welcome",
            start_time=base_time + timedelta(hours=4),
            end_time=base_time + timedelta(hours=5)
        )

        conflicts = find_schedule_conflicts(event)
        assert len(conflicts) == 1
        assert conflicts[0]['item_a']['id'] == str(item_a.id)
        assert conflicts[0]['item_b']['id'] == str(item_b.id)
