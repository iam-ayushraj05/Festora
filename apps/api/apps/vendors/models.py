import uuid
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from apps.events.models import Event


class VendorCategory(models.TextChoices):
    VENUE = "venue", "Venue & Hall"
    CATERING = "catering", "Catering & Beverages"
    PHOTOGRAPHY = "photography", "Photography & Video"
    MUSIC_DJ = "music_dj", "Music, DJ & Audio"
    DECOR_FLORAL = "decor_floral", "Decor, Lighting & Floral"
    PLANNING = "planning", "Event Planning & Coordination"
    TRANSPORTATION = "transportation", "Transportation & Logistics"
    OTHER = "other", "Other"


class Vendor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=VendorCategory.choices, default=VendorCategory.OTHER)
    contact_email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal("5.00"))
    price_range = models.CharField(max_length=10, default="$$")
    description = models.TextField(blank=True)
    sample_vendor = models.BooleanField(default=True)

    class Meta:
        ordering = ["category", "name"]

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class QuoteStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    RECEIVED = "received", "Quote Received"
    ACCEPTED = "accepted", "Accepted"
    DECLINED = "declined", "Declined"


class QuoteRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="quote_requests")
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="quote_requests")
    status = models.CharField(max_length=20, choices=QuoteStatus.choices, default=QuoteStatus.PENDING)
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Quote: {self.vendor.name} for {self.event.name}"


class BookingStatus(models.TextChoices):
    TENTATIVE = "tentative", "Tentative"
    CONFIRMED = "confirmed", "Confirmed"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"


class Booking(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="bookings")
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="bookings")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=BookingStatus.choices, default=BookingStatus.CONFIRMED)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    deposit_paid = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["start_time"]

    def __str__(self):
        return f"Booking: {self.vendor.name} ({self.status})"

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError({"end_time": "End time must be after start time."})

        # Booking conflict check
        if self.status in [BookingStatus.TENTATIVE, BookingStatus.CONFIRMED]:
            overlapping = Booking.objects.filter(
                vendor=self.vendor,
                status__in=[BookingStatus.TENTATIVE, BookingStatus.CONFIRMED],
                start_time__lt=self.end_time,
                end_time__gt=self.start_time,
            ).exclude(id=self.id)
            if overlapping.exists():
                raise ValidationError("This vendor is already booked for the specified timeframe.")
