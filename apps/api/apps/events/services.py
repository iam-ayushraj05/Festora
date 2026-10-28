from django.db import transaction
from .models import Event, EventMember, EventMemberRole, EventStatus

def duplicate_event(original_event: Event, user) -> Event:
    """Duplicate an existing event including its budget categories and tasks structure."""
    with transaction.atomic():
        new_event = Event.objects.create(
            name=f"{original_event.name} (Copy)",
            description=original_event.description,
            event_type=original_event.event_type,
            venue=original_event.venue,
            timezone=original_event.timezone,
            budget=original_event.budget,
            currency=original_event.currency,
            status=EventStatus.DRAFT,
        )
        # Set creator as Owner
        EventMember.objects.create(
            event=new_event,
            user=user,
            role=EventMemberRole.OWNER
        )

        # Clone budget categories
        for category in original_event.budget_categories.all():
            new_event.budget_categories.create(
                name=category.name,
                estimated_amount=category.estimated_amount
            )

        # Clone tasks
        for task in original_event.tasks.all():
            new_event.tasks.create(
                title=task.title,
                description=task.description,
                priority=task.priority,
                status='todo'
            )

        return new_event
