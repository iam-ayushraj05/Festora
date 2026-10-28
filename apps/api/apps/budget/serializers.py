from rest_framework import serializers

from .models import BudgetCategory, Expense


class ExpenseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Expense
        fields = [
            "id",
            "category",
            "category_name",
            "description",
            "amount",
            "currency",
            "date",
            "paid",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class BudgetCategorySerializer(serializers.ModelSerializer):
    expenses = ExpenseSerializer(many=True, read_only=True)
    total_spent = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = BudgetCategory
        fields = ["id", "event", "name", "estimated_amount", "total_spent", "expenses"]
        read_only_fields = ["id", "total_spent"]
