from rest_framework import serializers

from .models import Booking, QuoteRequest, Vendor


class VendorSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source="get_category_display", read_only=True)

    class Meta:
        model = Vendor
        fields = [
            "id",
            "name",
            "category",
            "category_display",
            "contact_email",
            "phone",
            "rating",
            "price_range",
            "description",
            "sample_vendor",
        ]


class QuoteRequestSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source="vendor.name", read_only=True)
    category = serializers.CharField(source="vendor.category", read_only=True)

    class Meta:
        model = QuoteRequest
        fields = [
            "id",
            "event",
            "vendor",
            "vendor_name",
            "category",
            "status",
            "estimated_cost",
            "message",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class BookingSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source="vendor.name", read_only=True)
    category = serializers.CharField(source="vendor.category", read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "event",
            "vendor",
            "vendor_name",
            "category",
            "start_time",
            "end_time",
            "status",
            "total_cost",
            "deposit_paid",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
