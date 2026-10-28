from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import GuestViewSet, PublicRSVPView

router = DefaultRouter()
router.register("", GuestViewSet, basename="guests")

urlpatterns = [
    path("rsvp/public/", PublicRSVPView.as_view(), name="public_rsvp"),
    path("", include(router.urls)),
]
