from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BudgetCategoryViewSet, ExpenseViewSet, BudgetSummaryView

router = DefaultRouter()
router.register('categories', BudgetCategoryViewSet, basename='budget_categories')
router.register('expenses', ExpenseViewSet, basename='expenses')

urlpatterns = [
    path('summary/<uuid:event_id>/', BudgetSummaryView.as_view(), name='budget_summary'),
    path('', include(router.urls)),
]
