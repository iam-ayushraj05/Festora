from rest_framework import permissions

from .models import EventMember, EventMemberRole


class IsEventMember(permissions.BasePermission):
    """Allows access only to authenticated users who are members of the event."""

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        event = getattr(obj, "event", obj)
        return EventMember.objects.filter(event=event, user=request.user).exists()


class IsEventOwner(permissions.BasePermission):
    """Allows access only to the event owner."""

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        event = getattr(obj, "event", obj)
        return EventMember.objects.filter(event=event, user=request.user, role=EventMemberRole.OWNER).exists()
