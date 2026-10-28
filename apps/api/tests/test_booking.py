from datetime import timedelta
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.events.models import Event
from apps.vendors.models import BookingStatus, Vendor, VendorCategory
from apps.vendors.services import create_booking_atomic


@pytest.mark.django_db
class TestBookingSecurity:
    def test_concurrent_booking(self):
        """T15: Transaction-level conflict prevention guarantees no double-booking."""
        vendor = Vendor.objects.create(name="Grand Ballroom", category=VendorCategory.VENUE)
        event1 = Event.objects.create(name="Event Alpha")
        event2 = Event.objects.create(name="Event Beta")

        start = timezone.now() + timedelta(days=10)
        end = start + timedelta(hours=6)

        # Booking 1 succeeds with atomic row locking
        b1 = create_booking_atomic(
            event=event1,
            vendor=vendor,
            start_time=start,
            end_time=end,
            total_cost=Decimal("2500.00"),
            status=BookingStatus.CONFIRMED,
        )
        assert b1.id is not None

        # Overlapping booking 2 is rejected
        with pytest.raises(ValidationError):
            create_booking_atomic(
                event=event2,
                vendor=vendor,
                start_time=start + timedelta(hours=1),
                end_time=end + timedelta(hours=2),
                status=BookingStatus.CONFIRMED,
            )
