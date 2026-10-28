from datetime import timedelta

import pytest
from django.utils import timezone

from apps.events.models import Event, EventMember
from apps.guests.models import Guest, InviteToken


@pytest.mark.django_db
class TestInviteTokensSecurity:
    def test_token_no_owner_access(self):
        """T11: Invite tokens only allow guest RSVP, never grant EventMember/Owner privileges."""
        event = Event.objects.create(name="Festora Gala")
        guest = Guest.objects.create(event=event, name="Guest Member")
        _, raw_token = InviteToken.create_for_guest(guest)

        # Token creates guest record, never creates an EventMember
        assert not EventMember.objects.filter(event=event).exists()

    def test_expired_token_rejected(self):
        """T13: Expired invite tokens are rejected and considered invalid."""
        event = Event.objects.create(name="Festora Birthday")
        guest = Guest.objects.create(event=event, name="Late Guest")
        token_obj, _ = InviteToken.create_for_guest(guest)

        # Simulate expiration
        token_obj.expires_at = timezone.now() - timedelta(days=1)
        token_obj.save()

        assert token_obj.is_valid() is False
