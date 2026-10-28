from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from apps.accounts.models import User
from apps.events.models import (
    Event,
    EventMember,
    EventMemberRole,
    EventStatus,
    EventType,
)
from apps.events.services import duplicate_event


@pytest.mark.django_db
class TestEvents:
    def test_event_state_machine_transitions(self):
        event = Event.objects.create(
            name="Summer Gala",
            event_type=EventType.COMMUNITY,
            status=EventStatus.DRAFT,
            budget=Decimal("5000.00"),
        )
        assert event.status == EventStatus.DRAFT

        # Valid transition: draft -> planning
        event.transition_to(EventStatus.PLANNING)
        assert event.status == EventStatus.PLANNING

        # Valid transition: planning -> confirmed
        event.transition_to(EventStatus.CONFIRMED)
        assert event.status == EventStatus.CONFIRMED

        # Valid transition: confirmed -> completed
        event.transition_to(EventStatus.COMPLETED)
        assert event.status == EventStatus.COMPLETED

        # Invalid transition: completed -> planning (raises ValidationError)
        with pytest.raises(ValidationError):
            event.transition_to(EventStatus.PLANNING)

    def test_negative_budget_rejected(self):
        event = Event(name="Invalid Event", budget=Decimal("-100.00"))
        with pytest.raises(ValidationError):
            event.clean()

    def test_duplicate_event(self):
        user = User.objects.create_user(email="owner@festora.test", password="Password123!")
        original = Event.objects.create(
            name="Grand Birthday",
            event_type=EventType.BIRTHDAY,
            budget=Decimal("2500.00"),
        )
        EventMember.objects.create(event=original, user=user, role=EventMemberRole.OWNER)

        copy = duplicate_event(original, user)
        assert copy.name == "Grand Birthday (Copy)"
        assert copy.status == EventStatus.DRAFT
        assert copy.budget == Decimal("2500.00")
        assert copy.members.filter(user=user, role=EventMemberRole.OWNER).exists()
