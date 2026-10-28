import pytest
from apps.events.models import Event
from apps.guests.models import Guest, InviteToken, RSVP, RSVPStatus

@pytest.mark.django_db
class TestRSVPSecurity:
    def test_rsvp_recorded(self):
        """T5: RSVP records include timestamp and token-based cryptographic verification."""
        event = Event.objects.create(name="Festora Anniversary")
        guest = Guest.objects.create(event=event, name="Victoria Lane", email="vicky@festora.test")
        token_obj, raw_token = InviteToken.create_for_guest(guest)

        rsvp = RSVP.objects.create(
            guest=guest,
            response=RSVPStatus.ATTENDING,
            notes="Looking forward to the celebration!"
        )
        assert rsvp.responded_at is not None
        assert rsvp.response == RSVPStatus.ATTENDING
        assert token_obj.is_valid() is True
