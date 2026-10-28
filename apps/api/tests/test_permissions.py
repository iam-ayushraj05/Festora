import pytest
from apps.accounts.models import User
from apps.events.models import Event, EventMember, EventMemberRole
from apps.events.permissions import IsEventMember, IsEventOwner

@pytest.mark.django_db
class TestPermissionsSecurity:
    def test_cross_user_access_denied(self):
        """T4: Access to other users' events denied by object permissions."""
        owner = User.objects.create_user(email="owner1@festora.test", password="Password123!")
        intruder = User.objects.create_user(email="intruder@festora.test", password="Password123!")

        event = Event.objects.create(name="Private Gala")
        EventMember.objects.create(event=event, user=owner, role=EventMemberRole.OWNER)

        class DummyRequest:
            def __init__(self, u):
                self.user = u

        perm = IsEventMember()
        assert perm.has_object_permission(DummyRequest(owner), None, event) is True
        assert perm.has_object_permission(DummyRequest(intruder), None, event) is False

    def test_role_escalation_denied(self):
        """T12: Co-host cannot perform owner-exclusive mutating actions."""
        owner = User.objects.create_user(email="legit_owner@festora.test", password="Password123!")
        cohost = User.objects.create_user(email="cohost_user@festora.test", password="Password123!")

        event = Event.objects.create(name="Wedding Celebration")
        EventMember.objects.create(event=event, user=owner, role=EventMemberRole.OWNER)
        EventMember.objects.create(event=event, user=cohost, role=EventMemberRole.COHOST)

        class DummyRequest:
            def __init__(self, u):
                self.user = u

        owner_perm = IsEventOwner()
        assert owner_perm.has_object_permission(DummyRequest(owner), None, event) is True
        assert owner_perm.has_object_permission(DummyRequest(cohost), None, event) is False
