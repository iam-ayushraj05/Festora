from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.events.permissions import IsEventMember

from .models import RSVP, Guest, InviteToken
from .serializers import GuestSerializer, PublicRSVPSubmitSerializer, RSVPSerializer
from .services import import_guests_from_csv, verify_and_get_guest_by_token


class GuestViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsEventMember]
    serializer_class = GuestSerializer

    def get_queryset(self):
        event_id = self.request.query_params.get("event")
        queryset = Guest.objects.filter(event__members__user=self.request.user).select_related(
            "event", "rsvp", "invite_token"
        )
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        return queryset.distinct()

    def perform_create(self, serializer):
        guest = serializer.save()
        InviteToken.create_for_guest(guest)

    @action(detail=True, methods=["post"])
    def generate_token(self, request, pk=None):
        guest = self.get_object()
        _, raw_token = InviteToken.create_for_guest(guest)
        return Response(
            {
                "guest_id": str(guest.id),
                "raw_token": raw_token,
                "invite_link": f"/rsvp?token={raw_token}",
            }
        )

    @action(detail=False, methods=["post"])
    def import_csv(self, request):
        event_id = request.data.get("event_id")
        csv_file = request.FILES.get("file")
        csv_text = request.data.get("csv_text")

        from apps.events.models import Event

        event = Event.objects.filter(id=event_id, members__user=request.user).first()
        if not event:
            return Response(
                {"error": "Event not found or unauthorized"},
                status=status.HTTP_404_NOT_FOUND,
            )

        content = ""
        if csv_file:
            content = csv_file.read().decode("utf-8", errors="ignore")
        elif csv_text:
            content = csv_text
        else:
            return Response(
                {"error": "No CSV file or text provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        count, errors = import_guests_from_csv(event, content)
        return Response({"created_count": count, "errors": errors})


class PublicRSVPView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        raw_token = request.query_params.get("token")
        if not raw_token:
            return Response({"error": "Token required"}, status=status.HTTP_400_BAD_REQUEST)
        guest = verify_and_get_guest_by_token(raw_token)
        if not guest:
            return Response(
                {"error": "Invalid or expired invitation token"},
                status=status.HTTP_404_NOT_FOUND,
            )

        rsvp = getattr(guest, "rsvp", None)
        return Response(
            {
                "guest": {
                    "id": str(guest.id),
                    "name": guest.name,
                    "email": guest.email,
                    "plus_ones": guest.plus_ones,
                    "dietary_requirements": guest.dietary_requirements,
                },
                "event": {
                    "id": str(guest.event.id),
                    "name": guest.event.name,
                    "venue": guest.event.venue,
                    "start_date": guest.event.start_date,
                    "event_type": guest.event.event_type,
                },
                "rsvp": RSVPSerializer(rsvp).data if rsvp else None,
            }
        )

    def post(self, request):
        serializer = PublicRSVPSubmitSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        raw_token = serializer.validated_data["token"]
        guest = verify_and_get_guest_by_token(raw_token)
        if not guest:
            return Response(
                {"error": "Invalid or expired invitation token"},
                status=status.HTTP_404_NOT_FOUND,
            )

        rsvp_status = serializer.validated_data["response"]
        notes = serializer.validated_data.get("notes", "")

        # Update optional guest details if provided
        if "plus_ones" in serializer.validated_data:
            guest.plus_ones = serializer.validated_data["plus_ones"]
        if "dietary_requirements" in serializer.validated_data:
            guest.dietary_requirements = serializer.validated_data["dietary_requirements"]
        guest.save()

        rsvp, created = RSVP.objects.update_or_create(
            guest=guest,
            defaults={
                "response": rsvp_status,
                "notes": notes,
                "responded_at": timezone.now(),
            },
        )
        return Response(
            {
                "message": "RSVP submitted successfully",
                "rsvp": RSVPSerializer(rsvp).data,
            }
        )
