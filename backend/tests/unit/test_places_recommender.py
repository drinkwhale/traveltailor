import asyncio
import sys
from types import SimpleNamespace

import pytest

pytestmark = pytest.mark.anyio("asyncio")


@pytest.fixture
def anyio_backend():
    return "asyncio"

sys.modules.setdefault('langchain.schema', SimpleNamespace(
    HumanMessage=SimpleNamespace,
    SystemMessage=SimpleNamespace,
    AIMessage=SimpleNamespace,
))

from src.schemas.travel_plan import TravelPlanCreate, TravelPreferences
from src.services.places.recommender import PlacesRecommender, RecommendationBundle
from src.services.ai.preference_analyzer import AnalyzedPreferences


async def test_google_results_cached(monkeypatch):
    recommender = PlacesRecommender()
    mock_client = type('Client', (), {})()

    async def fake_search_places(**_kwargs):
        await asyncio.sleep(0)
        return [
            {
                'name': 'Tokyo Tower',
                'geometry': {'location': {'lat': 35.6586, 'lng': 139.7454}},
                'formatted_address': '4 Chome-2-8 Shibakoen, Minato City, Tokyo',
                'rating': 4.6,
                'price_level': 2,
                'photos': [{'photo_reference': 'abc'}],
                'place_id': 'tokyo_tower',
            }
        ]

    mock_client.search_places = fake_search_places
    monkeypatch.setattr(recommender, '_maps_client', mock_client)

    cached_payloads = {}

    async def fake_cache_place(place_id, payload, ttl=None):
        cached_payloads[place_id] = payload

    monkeypatch.setattr('src.services.places.recommender.cache_place', fake_cache_place)

    plan = TravelPlanCreate(
        destination='Tokyo',
        country='Japan',
        start_date='2024-12-01',
        end_date='2024-12-05',
        budget_total=1000000,
        traveler_type='couple',
        traveler_count=2,
        preferences=TravelPreferences(),
    )
    bundle = RecommendationBundle(accommodations=[], activities=[], restaurants=[], cafes=[])
    preferences = AnalyzedPreferences(
        interests=['culture'],
        pace='normal',
        dietary_restrictions=[],
        traveler_persona='couple',
        themes=['culture'],
        focus_budget='moderate',
    )

    await recommender._augment_with_google(bundle, plan, preferences)

    assert any(place.external_id == 'tokyo_tower' for place in bundle.activities)
    assert 'tokyo_tower' in cached_payloads
