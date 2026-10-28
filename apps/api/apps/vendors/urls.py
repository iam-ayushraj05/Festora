from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BookingViewSet, QuoteRequestViewSet, VendorViewSet

router = DefaultRouter()
router.register("directory", VendorViewSet, basename="vendors_directory")
router.register("quotes", QuoteRequestViewSet, basename="vendor_quotes")
router.register("bookings", BookingViewSet, basename="vendor_bookings")

urlpatterns = [
    path("", include(router.urls)),
]
