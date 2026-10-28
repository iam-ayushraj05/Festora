from rest_framework import serializers
from .models import Guest, RSVP, InviteToken

class RSVPSerializer(serializers.ModelSerializer):
    class Meta:
        model = RSVP
        fields = ['id', 'response', 'notes', 'responded_at']
        read_only_fields = ['id', 'responded_at']

class GuestSerializer(serializers.ModelSerializer):
    rsvp = RSVPSerializer(read_only=True)
    invite_url = serializers.SerializerMethodField()

    class Meta:
        model = Guest
        fields = [
            'id', 'event', 'name', 'email', 'plus_ones',
            'dietary_requirements', 'accessibility_requirements',
            'created_at', 'rsvp', 'invite_url'
        ]
        read_only_fields = ['id', 'created_at']

    def get_invite_url(self, obj):
        # We don't expose raw tokens in list unless requested
        return f"/rsvp/guest/{obj.id}"

class PublicRSVPSubmitSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    response = serializers.ChoiceField(choices=['attending', 'declined', 'tentative'])
    notes = serializers.CharField(required=False, allow_blank=True)
    plus_ones = serializers.IntegerField(required=False, min_value=0)
    dietary_requirements = serializers.CharField(required=False, allow_blank=True)
