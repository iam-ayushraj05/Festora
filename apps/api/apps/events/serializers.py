from rest_framework import serializers
from .models import Event, EventMember, EventMemberRole

class EventMemberSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = EventMember
        fields = ['id', 'user', 'user_email', 'user_name', 'role', 'joined_at']
        read_only_fields = ['id', 'joined_at']

class EventSerializer(serializers.ModelSerializer):
    members = EventMemberSerializer(many=True, read_only=True)
    my_role = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'name', 'description', 'event_type', 'venue',
            'start_date', 'end_date', 'timezone', 'budget', 'currency',
            'status', 'created_at', 'updated_at', 'members', 'my_role'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_my_role(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            membership = obj.members.filter(user=request.user).first()
            return membership.role if membership else None
        return None

class EventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            'id', 'name', 'description', 'event_type', 'venue',
            'start_date', 'end_date', 'timezone', 'budget', 'currency', 'status'
        ]

    def create(self, validated_data):
        user = self.context['request'].user
        event = Event.objects.create(**validated_data)
        EventMember.objects.create(event=event, user=user, role=EventMemberRole.OWNER)
        return event
