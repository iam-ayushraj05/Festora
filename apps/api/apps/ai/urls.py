from django.urls import path

from .views import (
    AICopilotView,
    ApplySuggestionView,
    GenerateBudgetView,
    GenerateChecklistView,
    GenerateIdeasView,
    GenerateTimelineView,
)

urlpatterns = [
    path("generate-ideas/", GenerateIdeasView.as_view(), name="ai_generate_ideas"),
    path("generate-budget/", GenerateBudgetView.as_view(), name="ai_generate_budget"),
    path(
        "generate-timeline/",
        GenerateTimelineView.as_view(),
        name="ai_generate_timeline",
    ),
    path(
        "generate-checklist/",
        GenerateChecklistView.as_view(),
        name="ai_generate_checklist",
    ),
    path("copilot/", AICopilotView.as_view(), name="ai_copilot"),
    path("apply-suggestion/", ApplySuggestionView.as_view(), name="ai_apply_suggestion"),
]
