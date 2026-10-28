import uuid
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class EventType(models.TextChoices):
    WEDDING = "wedding", "Wedding"
    BIRTHDAY = "birthday", "Birthday"
    COMMUNITY = "community", "Community Event"
    CORPORATE = "corporate", "Corporate Event"
    ANNIVERSARY = "anniversary", "Anniversary"
    BABY_SHOWER = "baby_shower", "Baby Shower"
    OTHER = "other", "Other"


class EventStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PLANNING = "planning", "Planning"
    CONFIRMED = "confirmed", "Confirmed"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"


class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=50, choices=EventType.choices, default=EventType.OTHER)
    venue = models.CharField(max_length=255, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    timezone = models.CharField(max_length=50, default="UTC")
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=10, default="USD")
    status = models.CharField(max_length=20, choices=EventStatus.choices, default=EventStatus.PLANNING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "start_date"]),
            models.Index(fields=["event_type", "created_at"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_event_type_display()})"

    def clean(self):
        if self.budget < Decimal("0.00"):
            raise ValidationError({"budget": "Budget cannot be negative."})
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": "End date must be after start date."})

    def transition_to(self, new_status: str):
        allowed_transitions = {
            EventStatus.DRAFT: [EventStatus.PLANNING, EventStatus.CANCELLED],
            EventStatus.PLANNING: [EventStatus.CONFIRMED, EventStatus.CANCELLED],
            EventStatus.CONFIRMED: [EventStatus.COMPLETED, EventStatus.CANCELLED],
            EventStatus.COMPLETED: [],
            EventStatus.CANCELLED: [EventStatus.PLANNING],
        }
        valid_next = allowed_transitions.get(self.status, [])
        if new_status not in valid_next and new_status != self.status:
            raise ValidationError(f"Invalid transition from {self.status} to {new_status}")
        self.status = new_status
        self.save()


class EventMemberRole(models.TextChoices):
    OWNER = "owner", "Owner"
    COHOST = "cohost", "Co-Host"


class EventMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="event_memberships",
    )
    role = models.CharField(max_length=20, choices=EventMemberRole.choices, default=EventMemberRole.COHOST)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("event", "user")
        indexes = [
            models.Index(fields=["event", "role"]),
            models.Index(fields=["user", "role"]),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.event.name} ({self.role})"
