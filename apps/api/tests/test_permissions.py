import pytest
from apps.accounts.models import User
from apps.events.models import Event, EventMember, EventMemberRole
from apps.events.permissions import IsEventOwner, IsEventMember

@pytest.mark.django_db
class TestObjectPermissions:
    def test_owner_and_member_permissions(self):
        owner = User.objects.create_user(email='owner@test.com', password='Password123!')
        cohost = User.objects.create_user(email='cohost@test.com', password='Password123!')
        intruder = User.objects.create_user(email='intruder@test.com', password='Password123!')

        event = Event.objects.create(name="Festora VIP")
        EventMember.objects.create(event=event, user=owner, role=EventMemberRole.OWNER)
        EventMember.objects.create(event=event, user=cohost, role=EventMemberRole.COHOST)

        class DummyRequest:
            def __init__(self, u):
                self.user = u

        perm_member = IsEventMember()
        perm_owner = IsEventOwner()

        # Member checks
        assert perm_member.has_object_permission(DummyRequest(owner), None, event) is True
        assert perm_member.has_object_permission(DummyRequest(cohost), None, event) is True
        assert perm_member.has_object_permission(DummyRequest(intruder), None, event) is False

        # Owner checks
        assert perm_owner.has_object_permission(DummyRequest(owner), None, event) is True
        assert perm_owner.has_object_permission(DummyRequest(cohost), None, event) is False
        assert perm_owner.has_object_permission(DummyRequest(intruder), None, event) is False
