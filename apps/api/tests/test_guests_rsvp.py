import pytest
from apps.events.models import Event
from apps.guests.models import Guest, InviteToken, RSVP, RSVPStatus
from apps.guests.services import verify_and_get_guest_by_token, import_guests_from_csv

@pytest.mark.django_db
class TestGuestsAndRSVP:
    def test_invite_token_hashing_and_verification(self):
        event = Event.objects.create(name="Festora Gala")
        guest = Guest.objects.create(event=event, name="Alice Morgan", email="alice@festora.test")

        token_obj, raw_token = InviteToken.create_for_guest(guest)

        # Raw token must not equal persisted hash
        assert raw_token != token_obj.token_hash
        assert len(token_obj.token_hash) == 64  # SHA-256 length

        # Verification
        verified_guest = verify_and_get_guest_by_token(raw_token)
        assert verified_guest == guest

        # Invalid token returns None
        assert verify_and_get_guest_by_token("invalid-random-token") is None

    def test_public_rsvp_submission(self):
        event = Event.objects.create(name="Festora Wedding")
        guest = Guest.objects.create(event=event, name="Bob Smith")
        _, raw_token = InviteToken.create_for_guest(guest)

        verified = verify_and_get_guest_by_token(raw_token)
        assert verified is not None

        rsvp = RSVP.objects.create(guest=verified, response=RSVPStatus.ATTENDING, notes="Delighted!")
        assert rsvp.response == RSVPStatus.ATTENDING
        assert verified.rsvp.response == RSVPStatus.ATTENDING

    def test_csv_import(self):
        event = Event.objects.create(name="Community Carnival")
        csv_data = "name,email,plus_ones,dietary\nJohn Doe,john@test.com,1,Vegan\nJane Smith,jane@test.com,0,\n"

        created, errors = import_guests_from_csv(event, csv_data)
        assert created == 2
        assert len(errors) == 0
        assert event.guests.count() == 2
