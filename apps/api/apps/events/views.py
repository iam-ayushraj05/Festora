from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Event, EventMember, EventMemberRole
from .permissions import IsEventMember, IsEventOwner
from .serializers import EventCreateSerializer, EventMemberSerializer, EventSerializer
from .services import duplicate_event


class EventViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsEventMember]

    def get_queryset(self):
        return (
            Event.objects.filter(members__user=self.request.user)
            .prefetch_related("members", "members__user")
            .distinct()
        )

    def get_serializer_class(self):
        if self.action == "create":
            return EventCreateSerializer
        return EventSerializer

    def get_permissions(self):
        if self.action in ["destroy", "add_member", "remove_member"]:
            return [IsAuthenticated(), IsEventOwner()]
        return super().get_permissions()

    @action(detail=True, methods=["post"])
    def transition(self, request, pk=None):
        event = self.get_object()
        new_status = request.data.get("status")
        try:
            event.transition_to(new_status)
            return Response(EventSerializer(event, context={"request": request}).data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def duplicate(self, request, pk=None):
        original = self.get_object()
        new_event = duplicate_event(original, request.user)
        return Response(
            EventSerializer(new_event, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"])
    def add_member(self, request, pk=None):
        event = self.get_object()
        email = request.data.get("email")
        role = request.data.get("role", EventMemberRole.COHOST)
        from apps.accounts.models import User

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        member, created = EventMember.objects.get_or_create(event=event, user=user, defaults={"role": role})
        if not created:
            member.role = role
            member.save()
        return Response(EventMemberSerializer(member).data)
