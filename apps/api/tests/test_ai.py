import pytest
from decimal import Decimal
from apps.accounts.models import User
from apps.ai.models import AIRequest
from apps.ai.services import (
    check_and_record_rate_limit,
    generate_personalized_ideas,
    generate_budget_allocation,
    generate_timeline_run_of_show,
    generate_vendor_checklist
)

@pytest.mark.django_db
class TestAIAssistant:
    def test_ai_rate_limiting_enforcement(self):
        user = User.objects.create_user(email='ai_tester@festora.test', password='Password123!')

        # Simulate 50 requests
        for i in range(50):
            allowed = check_and_record_rate_limit(user, 'ideas', f'Prompt {i}')
            assert allowed is True

        # 51st request must be rejected
        allowed_51st = check_and_record_rate_limit(user, 'ideas', 'Over the limit prompt')
        assert allowed_51st is False

        # Logs must not store sensitive keys or full prompt secrets
        rate_limited_record = AIRequest.objects.filter(user=user, status='rate_limited').first()
        assert rate_limited_record is not None
        assert rate_limited_record.status == 'rate_limited'

    def test_personalized_ideas_generator(self):
        ideas = generate_personalized_ideas(event_type='wedding', vibe='luxury', guest_count=120)
        assert ideas['is_suggestion'] is True
        assert 'theme_title' in ideas['theme']
        assert len(ideas['theme']['palette']) > 0
        assert len(ideas['theme']['signature_cocktails']) > 0

    def test_budget_allocation_generator(self):
        budget = generate_budget_allocation(total_budget=Decimal('20000.00'), event_type='wedding')
        assert budget['is_suggestion'] is True
        assert len(budget['categories']) >= 5
        total_pct = sum(c['percentage'] for c in budget['categories'])
        assert 99.0 <= total_pct <= 101.0

    def test_timeline_run_of_show_generator(self):
        timeline = generate_timeline_run_of_show(event_type='birthday')
        assert timeline['is_suggestion'] is True
        assert len(timeline['items']) >= 6

    def test_vendor_checklist_generator(self):
        checklist = generate_vendor_checklist(event_type='community')
        assert checklist['is_suggestion'] is True
        assert len(checklist['checklist']) >= 4
