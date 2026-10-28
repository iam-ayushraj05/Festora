from decimal import Decimal

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.budget.models import BudgetCategory
from apps.events.models import Event
from apps.tasks.models import Task

from .services import (
    check_and_record_rate_limit,
    generate_budget_allocation,
    generate_personalized_ideas,
    generate_timeline_run_of_show,
    generate_vendor_checklist,
)


class GenerateIdeasView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        event_type = request.data.get("event_type", "wedding")
        vibe = request.data.get("vibe", "elegant")
        guest_count = int(request.data.get("guest_count", 50))

        if not check_and_record_rate_limit(request.user, "ideas", f"{event_type} - {vibe}"):
            return Response(
                {"error": "Daily AI rate limit reached (50 requests/day)."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        data = generate_personalized_ideas(event_type, vibe, guest_count)
        return Response(data)


class GenerateBudgetView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        event_type = request.data.get("event_type", "wedding")
        total_budget = Decimal(str(request.data.get("total_budget", "10000.00")))

        if not check_and_record_rate_limit(request.user, "budget", f"Budget {total_budget} for {event_type}"):
            return Response(
                {"error": "Daily AI rate limit reached (50 requests/day)."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        data = generate_budget_allocation(total_budget, event_type)
        return Response(data)


class GenerateTimelineView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        event_type = request.data.get("event_type", "wedding")

        if not check_and_record_rate_limit(request.user, "timeline", f"Timeline for {event_type}"):
            return Response(
                {"error": "Daily AI rate limit reached (50 requests/day)."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        data = generate_timeline_run_of_show(event_type=event_type)
        return Response(data)


class GenerateChecklistView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        event_type = request.data.get("event_type", "wedding")

        if not check_and_record_rate_limit(request.user, "checklist", f"Checklist for {event_type}"):
            return Response(
                {"error": "Daily AI rate limit reached (50 requests/day)."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        data = generate_vendor_checklist(event_type=event_type)
        return Response(data)


class AICopilotView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        prompt = request.data.get("prompt", "").strip()
        event_type = request.data.get("event_type", "wedding")

        if not prompt:
            return Response({"error": "Prompt is required"}, status=status.HTTP_400_BAD_REQUEST)

        if not check_and_record_rate_limit(request.user, "copilot", prompt[:100]):
            return Response(
                {"error": "Daily AI rate limit reached (50 requests/day)."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        # Smart conversational response based on prompt
        response_text = ""
        prompt_lower = prompt.lower()
        if "budget" in prompt_lower or "save" in prompt_lower or "cost" in prompt_lower:
            response_text = (
                "Here are top 3 insider tips to optimize your celebration budget:\n"
                "1. Choose in-season local florals and greenery garlands instead of imported exotic stems (saves ~30% on decor).\n"
                "2. Opt for signature his/her cocktails and beer/wine instead of an unrestricted top-shelf open bar.\n"
                "3. Consider a Friday evening or Sunday brunch celebration; venues frequently offer 15-25% discounts compared to Saturday night slots."
            )
        elif "rain" in prompt_lower or "weather" in prompt_lower or "emergency" in prompt_lower:
            response_text = (
                "For seamless rain and weather contingency planning:\n"
                "1. Confirm clear-span marquee tent availability with your rental vendor 72 hours prior.\n"
                "2. Designate a cozy indoor transition space (such as a glass conservatory or fireside lounge) for backup cocktail hour.\n"
                "3. Have a supply of matching clear golf umbrellas on hand for dramatic, magazine-worthy rainy portrait photography!"
            )
        elif "invitation" in prompt_lower or "rsvp" in prompt_lower or "wording" in prompt_lower:
            response_text = (
                "Here is an elegant reminder template for pending RSVPs:\n\n"
                "'Hi [Name]! We are putting the final touches on our guest count and menu seating for Festora. "
                "We would love to celebrate with you—please let us know if you can make it by [Date] via your personalized link!'"
            )
        else:
            response_text = (
                f"As your Festora AI Event Assistant, I've analyzed your {event_type} requirements. "
                "I recommend finalizing your core vendor trio (Venue, Catering, and Photography) first, as their availability dictates "
                "the day-of timeline and over 70% of your total budget allocation."
            )

        return Response(
            {
                "is_suggestion": True,
                "reply": response_text,
                "suggested_actions": [
                    "Generate Budget Breakdown",
                    "Generate Run-of-Show Timeline",
                    "Generate Vendor Checklist",
                ],
            }
        )


class ApplySuggestionView(APIView):
    """Explicitly applies and persists AI-generated suggestions to the real database."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        event_id = request.data.get("event_id")
        suggestion_type = request.data.get("suggestion_type")  # 'budget' or 'checklist'
        items = request.data.get("items", [])

        event = Event.objects.filter(id=event_id, members__user=request.user).first()
        if not event:
            return Response(
                {"error": "Event not found or unauthorized"},
                status=status.HTTP_404_NOT_FOUND,
            )

        created_count = 0
        if suggestion_type == "budget":
            for item in items:
                name = item.get("name")
                estimated = Decimal(str(item.get("estimated_amount", "0.00")))
                if name:
                    BudgetCategory.objects.get_or_create(
                        event=event, name=name, defaults={"estimated_amount": estimated}
                    )
                    created_count += 1
        elif suggestion_type == "checklist":
            for item in items:
                task_title = item.get("task") or item.get("title")
                priority = item.get("priority", "medium")
                if task_title:
                    Task.objects.create(event=event, title=task_title, priority=priority, status="todo")
                    created_count += 1

        return Response(
            {
                "message": f"Successfully applied {created_count} items from AI suggestion.",
                "applied_count": created_count,
            }
        )
