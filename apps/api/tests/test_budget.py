import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from apps.events.models import Event
from apps.budget.models import BudgetCategory, Expense
from apps.budget.services import calculate_event_budget_summary

@pytest.mark.django_db
class TestBudget:
    def test_decimal_precision_and_negative_rejection(self):
        event = Event.objects.create(name="Festora Budget Test", budget=Decimal('10000.00'))
        category = BudgetCategory.objects.create(event=event, name="Catering", estimated_amount=Decimal('5000.00'))

        expense = Expense.objects.create(
            category=category,
            description="Hors d'oeuvres",
            amount=Decimal('1234.56')
        )
        assert expense.amount == Decimal('1234.56')
        assert category.total_spent == Decimal('1234.56')

        # Negative or zero expense rejected
        bad_expense = Expense(category=category, description="Bad", amount=Decimal('-50.00'))
        with pytest.raises(ValidationError):
            bad_expense.clean()

    def test_budget_summary_calculations(self):
        event = Event.objects.create(name="Festora Anniversary", budget=Decimal('5000.00'))
        cat1 = BudgetCategory.objects.create(event=event, name="Venue", estimated_amount=Decimal('3000.00'))
        cat2 = BudgetCategory.objects.create(event=event, name="Music", estimated_amount=Decimal('1500.00'))

        Expense.objects.create(category=cat1, description="Venue deposit", amount=Decimal('2000.00'))
        Expense.objects.create(category=cat2, description="DJ fee", amount=Decimal('1000.00'))

        summary = calculate_event_budget_summary(event)
        assert summary['total_budget'] == '5000.00'
        assert summary['total_spent'] == '3000.00'
        assert summary['remaining_budget'] == '2000.00'
        assert summary['is_over_budget'] is False
        assert summary['utilization_percentage'] == 60.0
