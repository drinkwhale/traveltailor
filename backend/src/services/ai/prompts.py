"""Prompt templates for AI travel planning"""

from __future__ import annotations

from textwrap import dedent

from ...schemas.travel_plan import TravelPlanCreate, TravelPreferences


SYSTEM_PROMPT = dedent(
    """
    You are TravelTailor, an award-winning travel concierge.
    Produce balanced, budget-conscious itineraries that mix culture, cuisine, and rest time.
    Always consider weather, travel distance, and traveler preferences.
    Respond with structured JSON so the application can parse the plan.
    """
)


def build_plan_prompt(plan: TravelPlanCreate, preferences: TravelPreferences) -> str:
    """Generate the user prompt for AI plan generation."""

    interests = ", ".join(preferences.interests) if preferences.interests else "general sights"
    must_have = ", ".join(preferences.must_have) if preferences.must_have else "none"
    avoid = ", ".join(preferences.avoid) if preferences.avoid else "none"
    dietary = (
        ", ".join(preferences.dietary_restrictions)
        if preferences.dietary_restrictions
        else "no specific restrictions"
    )

    return dedent(
        f"""
        Destination: {plan.destination}, {plan.country}
        Travel dates: {plan.start_date.isoformat()} to {plan.end_date.isoformat()}
        Travelers: {plan.traveler_count} ({plan.traveler_type})
        Total budget: {plan.budget_total} KRW
        Pace: {preferences.pace}
        Interests: {interests}
        Must-have experiences: {must_have}
        Avoid: {avoid}
        Dietary notes: {dietary}
        Additional notes: {preferences.notes or 'none'}
        """
    ).strip()

