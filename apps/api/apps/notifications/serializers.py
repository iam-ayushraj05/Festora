from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    event_name = serializers.CharField(source='event.name', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'event', 'event_name', 'title', 'message', 'read', 'created_at']
        read_only_fields = ['id', 'created_at']
