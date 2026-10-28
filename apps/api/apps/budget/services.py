from decimal import Decimal
from typing import Any

from apps.events.models import Event


def calculate_event_budget_summary(event: Event) -> dict[str, Any]:
    """Calculate fixed-precision financial summary for an event."""
    total_budget = event.budget
    categories = event.budget_categories.prefetch_related("expenses").all()

    total_estimated = sum((cat.estimated_amount for cat in categories), Decimal("0.00"))
    total_spent = Decimal("0.00")
    category_summaries = []

    for cat in categories:
        cat_expenses = list(cat.expenses.all())
        cat_spent = sum((exp.amount for exp in cat_expenses), Decimal("0.00"))
        total_spent += cat_spent
        category_summaries.append(
            {
                "id": str(cat.id),
                "name": cat.name,
                "estimated_amount": str(cat.estimated_amount),
                "spent_amount": str(cat_spent),
                "remaining": str(cat.estimated_amount - cat_spent),
                "expense_count": len(cat_expenses),
            }
        )

    remaining_budget = total_budget - total_spent
    utilization_pct = round((total_spent / total_budget * 100), 2) if total_budget > 0 else 0.0

    # Confirmed guests calculation
    confirmed_guests = event.guests.filter(rsvp__response="attending").count()
    cost_per_guest = round(total_spent / confirmed_guests, 2) if confirmed_guests > 0 else Decimal("0.00")

    return {
        "total_budget": str(total_budget),
        "currency": event.currency,
        "total_estimated": str(total_estimated),
        "total_spent": str(total_spent),
        "remaining_budget": str(remaining_budget),
        "is_over_budget": total_spent > total_budget,
        "utilization_percentage": float(utilization_pct),
        "confirmed_guests_count": confirmed_guests,
        "cost_per_guest": str(cost_per_guest),
        "categories": category_summaries,
    }
