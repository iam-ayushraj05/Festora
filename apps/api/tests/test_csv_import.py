import pytest

from apps.events.models import Event
from apps.guests.services import import_guests_from_csv


@pytest.mark.django_db
class TestCSVImportSecurity:
    def test_row_limit(self):
        """T10: CSV import safely parses streamed rows and returns row-by-row error validation."""
        event = Event.objects.create(name="Festora Community Day")

        # Stream valid and invalid rows
        csv_data = "name,email,plus_ones\nValid Guest,valid@test.com,2\n,missingname@test.com,0\n"
        count, errors = import_guests_from_csv(event, csv_data)

        assert count == 1
        assert len(errors) == 1
        assert errors[0]["row"] == 3
        assert "Name is required" in errors[0]["error"]
