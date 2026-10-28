from rest_framework import serializers

from .models import ScheduleItem, Task


class TaskSerializer(serializers.ModelSerializer):
    assigned_to_email = serializers.EmailField(source="assigned_to.email", read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "event",
            "assigned_to",
            "assigned_to_email",
            "title",
            "description",
            "priority",
            "status",
            "due_date",
            "completed_at",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ScheduleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleItem
        fields = [
            "id",
            "event",
            "title",
            "description",
            "location",
            "start_time",
            "end_time",
        ]
        read_only_fields = ["id"]

    def validate(self, attrs):
        start = attrs.get("start_time")
        end = attrs.get("end_time")
        if start and end and end <= start:
            raise serializers.ValidationError({"end_time": "End time must be after start time."})
        return attrs
