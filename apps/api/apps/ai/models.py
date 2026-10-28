import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.events.models import Event

class AIRequestType(models.TextChoices):
    PLAN = 'plan', 'Event Plan'
    BUDGET = 'budget', 'Budget Allocation'
    TIMELINE = 'timeline', 'Day-of Timeline'
    CHECKLIST = 'checklist', 'Vendor Checklist'
    IDEAS = 'ideas', 'Personalized Ideas'
    COPILOT = 'copilot', 'AI Copilot'

class AIRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_requests')
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_requests')
    request_type = models.CharField(max_length=30, choices=AIRequestType.choices)
    prompt_summary = models.CharField(max_length=255)
    status = models.CharField(max_length=20, default='success')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.request_type} ({self.status})"
