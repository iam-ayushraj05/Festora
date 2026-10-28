from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.events.permissions import IsEventMember

from .models import Booking, QuoteRequest, Vendor
from .serializers import BookingSerializer, QuoteRequestSerializer, VendorSerializer


class VendorViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer

    def get_queryset(self):
        category = self.request.query_params.get("category")
        queryset = Vendor.objects.all()
        if category:
            queryset = queryset.filter(category=category)
        return queryset


class QuoteRequestViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsEventMember]
    serializer_class = QuoteRequestSerializer

    def get_queryset(self):
        event_id = self.request.query_params.get("event")
        queryset = QuoteRequest.objects.filter(
            event__members__user=self.request.user
        ).select_related("event", "vendor")
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        return queryset.distinct()


class BookingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsEventMember]
    serializer_class = BookingSerializer

    def get_queryset(self):
        event_id = self.request.query_params.get("event")
        queryset = Booking.objects.filter(
            event__members__user=self.request.user
        ).select_related("event", "vendor")
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        return queryset.distinct()
