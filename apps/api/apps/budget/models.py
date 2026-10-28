import uuid
from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.events.models import Event

class BudgetCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='budget_categories')
    name = models.CharField(max_length=100)
    estimated_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Budget categories'

    def __str__(self):
        return f"{self.name} - {self.event.name}"

    def clean(self):
        if self.estimated_amount < Decimal('0.00'):
            raise ValidationError({'estimated_amount': 'Estimated amount cannot be negative.'})

    @property
    def total_spent(self) -> Decimal:
        total = self.expenses.aggregate(models.Sum('amount'))['amount__sum']
        return total or Decimal('0.00')

class Expense(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(BudgetCategory, on_delete=models.CASCADE, related_name='expenses')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD')
    date = models.DateField(default=timezone.now)
    paid = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.description}: {self.amount} {self.currency}"

    def clean(self):
        if self.amount <= Decimal('0.00'):
            raise ValidationError({'amount': 'Expense amount must be strictly greater than zero.'})
