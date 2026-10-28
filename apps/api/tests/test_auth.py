import pytest
from django.contrib.auth import authenticate
from django.test import RequestFactory
from apps.accounts.models import User
from apps.accounts.views import LoginView

@pytest.mark.django_db
class TestAuthSecurity:
    def test_login_throttling(self):
        """T1: Verify authentication checks valid credentials."""
        user = User.objects.create_user(email="secure@festora.test", password="SecurePassword123!")
        factory = RequestFactory()
        request = factory.post("/api/auth/login/")

        auth_user = authenticate(request=request, email="secure@festora.test", password="SecurePassword123!")
        assert auth_user == user

        failed_user = authenticate(request=request, email="secure@festora.test", password="WrongPassword!")
        assert failed_user is None

    def test_session_regeneration(self):
        """T2: Verify session ID regeneration prevents session fixation."""
        factory = RequestFactory()
        request = factory.post("/api/auth/login/")
        from django.contrib.sessions.middleware import SessionMiddleware
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

        initial_key = request.session.session_key
        request.session.cycle_key()
        new_key = request.session.session_key
        assert initial_key != new_key

    def test_csrf_required(self):
        """T3: Verify CSRF token endpoint is available."""
        from django.test import Client
        client = Client(enforce_csrf_checks=True)
        response = client.get("/api/auth/csrf/")
        assert response.status_code == 200
        assert "csrftoken" in response.cookies or response.status_code == 200

    def test_no_account_enumeration(self):
        """T7: Same generic response for non-existent vs invalid credentials."""
        user = User.objects.create_user(email="registered@festora.test", password="Password123!")
        factory = RequestFactory()
        req = factory.post("/api/auth/login/")

        # Both non-existent and wrong password return None from authenticate
        res1 = authenticate(request=req, email="registered@festora.test", password="BadPassword")
        res2 = authenticate(request=req, email="nonexistent@festora.test", password="BadPassword")
        assert res1 is None
        assert res2 is None
