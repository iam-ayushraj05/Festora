from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import BudgetCategory, Expense
from .serializers import BudgetCategorySerializer, ExpenseSerializer
from .services import calculate_event_budget_summary
from apps.events.models import Event
from apps.events.permissions import IsEventMember

class BudgetCategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsEventMember]
    serializer_class = BudgetCategorySerializer

    def get_queryset(self):
        event_id = self.request.query_params.get('event')
        queryset = BudgetCategory.objects.filter(event__members__user=self.request.user)
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        return queryset.distinct()

class ExpenseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsEventMember]
    serializer_class = ExpenseSerializer

    def get_queryset(self):
        event_id = self.request.query_params.get('event')
        queryset = Expense.objects.filter(category__event__members__user=self.request.user)
        if event_id:
            queryset = queryset.filter(category__event_id=event_id)
        return queryset.distinct()

class BudgetSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, event_id):
        event = Event.objects.filter(id=event_id, members__user=request.user).first()
        if not event:
            return Response({'error': 'Event not found or unauthorized'}, status=status.HTTP_404_NOT_FOUND)
        summary = calculate_event_budget_summary(event)
        return Response(summary)
