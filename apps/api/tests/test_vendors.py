import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from apps.events.models import Event
from apps.vendors.models import Vendor, VendorCategory, Booking, BookingStatus, QuoteRequest, QuoteStatus

@pytest.mark.django_db
class TestVendorsAndBookings:
    def test_vendor_creation_and_quotes(self):
        vendor = Vendor.objects.create(
            name="Starlight Photo & Film",
            category=VendorCategory.PHOTOGRAPHY,
            rating=Decimal('4.90'),
            price_range='$$'
        )
        event = Event.objects.create(name="Wedding Celebration")

        quote = QuoteRequest.objects.create(
            event=event,
            vendor=vendor,
            status=QuoteStatus.PENDING,
            estimated_cost=Decimal('2200.00'),
            message="Need 8 hours of coverage"
        )
        assert quote.vendor.name == "Starlight Photo & Film"
        assert quote.estimated_cost == Decimal('2200.00')

    def test_booking_overlap_prevention(self):
        vendor = Vendor.objects.create(name="Grand Hall", category=VendorCategory.VENUE)
        event1 = Event.objects.create(name="Event 1")
        event2 = Event.objects.create(name="Event 2")

        base_time = timezone.now().replace(minute=0, second=0, microsecond=0)

        # Booking 1: 10:00 - 15:00
        Booking.objects.create(
            event=event1,
            vendor=vendor,
            start_time=base_time,
            end_time=base_time + timedelta(hours=5),
            status=BookingStatus.CONFIRMED
        )

        # Booking 2 for same vendor overlapping: 12:00 - 18:00
        booking2 = Booking(
            event=event2,
            vendor=vendor,
            start_time=base_time + timedelta(hours=2),
            end_time=base_time + timedelta(hours=8),
            status=BookingStatus.CONFIRMED
        )

        with pytest.raises(ValidationError):
            booking2.clean()
