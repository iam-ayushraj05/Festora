from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BudgetCategoryViewSet, BudgetSummaryView, ExpenseViewSet

router = DefaultRouter()
router.register("categories", BudgetCategoryViewSet, basename="budget_categories")
router.register("expenses", ExpenseViewSet, basename="expenses")

urlpatterns = [
    path("summary/<uuid:event_id>/", BudgetSummaryView.as_view(), name="budget_summary"),
    path("", include(router.urls)),
]
