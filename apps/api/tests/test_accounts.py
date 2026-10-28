import pytest

from apps.accounts.models import User


@pytest.mark.django_db
class TestAccounts:
    def test_create_user(self):
        user = User.objects.create_user(
            email="testuser@festora.test",
            password="TestPassword123!",
            first_name="Festora",
            last_name="Tester",
        )
        assert user.email == "testuser@festora.test"
        assert user.check_password("TestPassword123!")
        assert not user.is_staff
        assert user.full_name == "Festora Tester"

    def test_create_superuser(self):
        admin = User.objects.create_superuser(email="admin@festora.test", password="AdminPassword123!")
        assert admin.is_staff
        assert admin.is_superuser
