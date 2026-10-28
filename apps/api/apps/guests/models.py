import uuid
import secrets
import hashlib
from datetime import timedelta
from django.db import models
from django.utils import timezone
from apps.events.models import Event

class Guest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='guests')
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    plus_ones = models.PositiveIntegerField(default=0)
    dietary_requirements = models.CharField(max_length=255, blank=True)
    accessibility_requirements = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.event.name})"

class RSVPStatus(models.TextChoices):
    ATTENDING = 'attending', 'Attending'
    DECLINED = 'declined', 'Declined'
    TENTATIVE = 'tentative', 'Tentative'

class RSVP(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    guest = models.OneToOneField(Guest, on_delete=models.CASCADE, related_name='rsvp')
    response = models.CharField(max_length=20, choices=RSVPStatus.choices, default=RSVPStatus.ATTENDING)
    notes = models.TextField(blank=True)
    responded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.guest.name} - {self.response}"

class InviteToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    guest = models.OneToOneField(Guest, on_delete=models.CASCADE, related_name='invite_token')
    token_hash = models.CharField(max_length=64, unique=True, db_index=True)
    expires_at = models.DateTimeField()
    revoked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create_for_guest(cls, guest: Guest, days_valid: int = 30) -> tuple['InviteToken', str]:
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode('utf-8')).hexdigest()
        expires_at = timezone.now() + timedelta(days=days_valid)
        cls.objects.filter(guest=guest).delete()
        token_obj = cls.objects.create(
            guest=guest,
            token_hash=token_hash,
            expires_at=expires_at,
            revoked=False
        )
        return token_obj, raw_token

    def is_valid(self) -> bool:
        return not self.revoked and self.expires_at > timezone.now()
