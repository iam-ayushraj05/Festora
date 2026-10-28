from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from .models import Booking, BookingStatus, Vendor
from apps.events.models import Event

def create_booking_atomic(
    event: Event,
    vendor: Vendor,
    start_time,
    end_time,
    total_cost: Decimal = Decimal("0.00"),
    deposit_paid: Decimal = Decimal("0.00"),
    status: str = BookingStatus.CONFIRMED,
) -> Booking:
    """
    Creates a booking using transaction isolation and row locking (select_for_update)
    to guarantee no concurrent double-booking race conditions.
    """
    if end_time <= start_time:
        raise ValidationError({"end_time": "End time must be after start time."})

    with transaction.atomic():
        # Lock the vendor row to serialize concurrent booking attempts
        locked_vendor = Vendor.objects.select_for_update().get(id=vendor.id)

        if status in [BookingStatus.TENTATIVE, BookingStatus.CONFIRMED]:
            overlapping = Booking.objects.filter(
                vendor=locked_vendor,
                status__in=[BookingStatus.TENTATIVE, BookingStatus.CONFIRMED],
                start_time__lt=end_time,
                end_time__gt=start_time,
            ).exists()

            if overlapping:
                raise ValidationError("This vendor is already booked for the specified timeframe.")

        booking = Booking.objects.create(
            event=event,
            vendor=locked_vendor,
            start_time=start_time,
            end_time=end_time,
            status=status,
            total_cost=total_cost,
            deposit_paid=deposit_paid,
        )
        return booking

def check_vendor_availability(vendor: Vendor, start_time, end_time, exclude_booking_id=None) -> bool:
    """Quick indexed availability check for vendor booking window."""
    qs = Booking.objects.filter(
        vendor=vendor,
        status__in=[BookingStatus.TENTATIVE, BookingStatus.CONFIRMED],
        start_time__lt=end_time,
        end_time__gt=start_time,
    )
    if exclude_booking_id:
        qs = qs.exclude(id=exclude_booking_id)
    return not qs.exists()
