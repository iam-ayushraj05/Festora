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
        EventMember.objects.create(event=new_event, user=user, role=EventMemberRole.OWNER)

        # Bulk clone budget categories
        from apps.budget.models import BudgetCategory
        from apps.tasks.models import Task, TaskStatus

        categories_to_create = [
            BudgetCategory(event=new_event, name=cat.name, estimated_amount=cat.estimated_amount)
            for cat in original_event.budget_categories.all()
        ]
        if categories_to_create:
            BudgetCategory.objects.bulk_create(categories_to_create)

        # Bulk clone tasks
        tasks_to_create = [
            Task(
                event=new_event,
                title=task.title,
                description=task.description,
                priority=task.priority,
                status=TaskStatus.TODO,
            )
            for task in original_event.tasks.all()
        ]
        if tasks_to_create:
            Task.objects.bulk_create(tasks_to_create)

        return new_event
