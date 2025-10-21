"""Place recommendation heuristics"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Iterable

from ...config.settings import settings
from ...integrations.google_maps import get_google_maps_client
from ...schemas.place import PlaceCreate
from ...schemas.travel_plan import TravelPlanCreate
from ..ai.preference_analyzer import AnalyzedPreferences


@dataclass
class RecommendationBundle:
    """Collection of recommended places grouped by type"""

    accommodations: list[PlaceCreate]
    activities: list[PlaceCreate]
    restaurants: list[PlaceCreate]
    cafes: list[PlaceCreate]
    warnings: list[str] = field(default_factory=list)

    def all_places(self) -> Iterable[PlaceCreate]:
        yield from self.accommodations
        yield from self.activities
        yield from self.restaurants
        yield from self.cafes


SAMPLE_DATA = {
    "tokyo": RecommendationBundle(
        accommodations=[
            PlaceCreate(
                name="Shinjuku Granbell Hotel",
                category="accommodation",
                latitude=35.6938,
                longitude=139.7034,
                address="2-14-5 Kabukicho, Shinjuku-ku, Tokyo",
                city="Tokyo",
                country="Japan",
                rating=4.2,
                tags=["boutique", "nightlife"],
                external_id="tokyo_accommodation_1",
                external_source="seed",
            )
        ],
        activities=[
            PlaceCreate(
                name="Senso-ji Temple",
                category="attraction",
                latitude=35.7148,
                longitude=139.7967,
                address="2-3-1 Asakusa, Taito-ku, Tokyo",
                city="Tokyo",
                country="Japan",
                rating=4.7,
                tags=["culture", "historic"],
                external_id="tokyo_activity_1",
                external_source="seed",
            ),
            PlaceCreate(
                name="teamLab Borderless",
                category="attraction",
                latitude=35.6276,
                longitude=139.7798,
                address="1-3-8 Aomi, Koto City, Tokyo",
                city="Tokyo",
                country="Japan",
                rating=4.6,
                tags=["art", "digital"],
                external_id="tokyo_activity_2",
                external_source="seed",
            ),
            PlaceCreate(
                name="Meiji Shrine",
                category="attraction",
                latitude=35.6764,
                longitude=139.6993,
                address="1-1 Yoyogikamizonocho, Shibuya City, Tokyo",
                city="Tokyo",
                country="Japan",
                rating=4.6,
                tags=["shrine", "nature"],
                external_id="tokyo_activity_3",
                external_source="seed",
            ),
        ],
        restaurants=[
            PlaceCreate(
                name="Ichiran Ramen Shinjuku",
                category="restaurant",
                latitude=35.6932,
                longitude=139.7030,
                address="1-22-7 Kabukicho, Shinjuku-ku, Tokyo",
                city="Tokyo",
                country="Japan",
                rating=4.4,
                tags=["ramen", "noodle"],
                external_id="tokyo_restaurant_1",
                external_source="seed",
            ),
            PlaceCreate(
                name="Sukiyabashi Jiro Roppongi",
                category="restaurant",
                latitude=35.6617,
                longitude=139.7326,
                address="Roppongi Hills, 6-12-2 Roppongi, Minato City, Tokyo",
                city="Tokyo",
                country="Japan",
                rating=4.5,
                tags=["sushi", "fine-dining"],
                external_id="tokyo_restaurant_2",
                external_source="seed",
            ),
            PlaceCreate(
                name="Tsukiji Outer Market",
                category="restaurant",
                latitude=35.6654,
                longitude=139.7708,
                address="4-16-2 Tsukiji, Chuo City, Tokyo",
                city="Tokyo",
                country="Japan",
                rating=4.3,
                tags=["seafood", "street-food"],
                external_id="tokyo_restaurant_3",
                external_source="seed",
            ),
        ],
        cafes=[
            PlaceCreate(
                name="Blue Bottle Coffee Aoyama",
                category="cafe",
                latitude=35.6635,
                longitude=139.7083,
                address="3-13-14 Minamiaoyama, Minato City, Tokyo",
                city="Tokyo",
                country="Japan",
                rating=4.4,
                tags=["coffee", "minimal"],
                external_id="tokyo_cafe_1",
                external_source="seed",
            )
        ],
    ),
    "seoul": RecommendationBundle(
        accommodations=[
            PlaceCreate(
                name="L7 Myeongdong",
                category="accommodation",
                latitude=37.5636,
                longitude=126.9852,
                address="137 Toegye-ro, Jung-gu, Seoul",
                city="Seoul",
                country="South Korea",
                rating=4.3,
                tags=["shopping", "central"],
                external_id="seoul_accommodation_1",
                external_source="seed",
            )
        ],
        activities=[
            PlaceCreate(
                name="Gyeongbokgung Palace",
                category="attraction",
                latitude=37.5796,
                longitude=126.9770,
                address="161 Sajik-ro, Jongno-gu, Seoul",
                city="Seoul",
                country="South Korea",
                rating=4.6,
                tags=["palace", "history"],
                external_id="seoul_activity_1",
                external_source="seed",
            ),
            PlaceCreate(
                name="Bukchon Hanok Village",
                category="attraction",
                latitude=37.5826,
                longitude=126.9830,
                address="37 Gyedong-gil, Jongno-gu, Seoul",
                city="Seoul",
                country="South Korea",
                rating=4.4,
                tags=["traditional", "culture"],
                external_id="seoul_activity_2",
                external_source="seed",
            ),
        ],
        restaurants=[
            PlaceCreate(
                name="Jinju Jip",
                category="restaurant",
                latitude=37.5659,
                longitude=126.9830,
                address="24-15 Chungmuro 1(il)-ga, Jung-gu, Seoul",
                city="Seoul",
                country="South Korea",
                rating=4.4,
                tags=["galbitang", "korean"],
                external_id="seoul_restaurant_1",
                external_source="seed",
            ),
            PlaceCreate(
                name="Tosokchon Samgyetang",
                category="restaurant",
                latitude=37.5790,
                longitude=126.9716,
                address="5 Jahamun-ro 5-gil, Jongno-gu, Seoul",
                city="Seoul",
                country="South Korea",
                rating=4.3,
                tags=["samgyetang", "heritage"],
                external_id="seoul_restaurant_2",
                external_source="seed",
            ),
        ],
        cafes=[
            PlaceCreate(
                name="Onion Anguk",
                category="cafe",
                latitude=37.5795,
                longitude=126.9860,
                address="5 Gye-dong, Jongno-gu, Seoul",
                city="Seoul",
                country="South Korea",
                rating=4.5,
                tags=["bakery", "hanok"],
                external_id="seoul_cafe_1",
                external_source="seed",
            )
        ],
    ),
}


def _fallback_bundle(destination: str, country: str) -> RecommendationBundle:
    return RecommendationBundle(
        accommodations=[
            PlaceCreate(
                name=f"Central Boutique Stay {destination}",
                category="accommodation",
                latitude=0.0,
                longitude=0.0,
                address=f"Downtown {destination}",
                city=destination,
                country=country,
                rating=4.0,
                tags=["central"],
                external_id=f"generic_accommodation_{destination}",
                external_source="seed",
            )
        ],
        activities=[
            PlaceCreate(
                name=f"Guided City Walking Tour {destination}",
                category="attraction",
                latitude=0.01,
                longitude=0.01,
                address=destination,
                city=destination,
                country=country,
                rating=4.2,
                tags=["culture"],
                external_id=f"generic_activity_{destination}",
                external_source="seed",
            )
        ],
        restaurants=[
            PlaceCreate(
                name=f"Local Eats {destination}",
                category="restaurant",
                latitude=0.02,
                longitude=0.02,
                address=destination,
                city=destination,
                country=country,
                rating=4.0,
                tags=["local"],
                external_id=f"generic_restaurant_{destination}",
                external_source="seed",
            )
        ],
        cafes=[
            PlaceCreate(
                name=f"Coffee Corner {destination}",
                category="cafe",
                latitude=0.03,
                longitude=0.03,
                address=destination,
                city=destination,
                country=country,
                rating=4.1,
                tags=["coffee"],
                external_id=f"generic_cafe_{destination}",
                external_source="seed",
            )
        ],
    )


class PlacesRecommender:
    """Return curated place suggestions, optionally enriched via Google Places"""

    def __init__(self) -> None:
        self._maps_client = None
        if settings.GOOGLE_MAPS_API_KEY:
            try:
                self._maps_client = get_google_maps_client()
            except Exception:
                self._maps_client = None

    async def _augment_with_google(
        self,
        bundle: RecommendationBundle,
        plan: TravelPlanCreate,
        preferences: AnalyzedPreferences,
    ) -> None:
        if not self._maps_client:
            return

        try:
            tasks = [
                self._maps_client.search_places(
                    query=f"best {interest} {plan.destination}",
                    place_type="tourist_attraction",
                    language="en",
                )
                for interest in preferences.interests[:2]
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        except Exception:
            bundle.warnings.append("Google Places 데이터를 가져오지 못했습니다. 로컬 추천을 사용합니다.")
            return

        for result in results:
            if isinstance(result, Exception):
                bundle.warnings.append("일부 장소 데이터를 가져오지 못했습니다.")
                continue
            for item in result[:2]:
                bundle.activities.append(
                    PlaceCreate(
                        name=item.get("name", "Curated Spot"),
                        category="attraction",
                        latitude=item.get("geometry", {})
                        .get("location", {})
                        .get("lat", 0.0),
                        longitude=item.get("geometry", {})
                        .get("location", {})
                        .get("lng", 0.0),
                        address=item.get("formatted_address"),
                        city=plan.destination,
                        country=plan.country,
                        rating=item.get("rating"),
                        price_level=item.get("price_level"),
                        photos=[photo.get("photo_reference") for photo in item.get("photos", [])]
                        if item.get("photos")
                        else None,
                        tags=["google"],
                        external_id=item.get("place_id"),
                        external_source="google_places",
                    )
                )

    async def recommend(
        self,
        plan: TravelPlanCreate,
        preferences: AnalyzedPreferences,
    ) -> RecommendationBundle:
        key = plan.destination.lower()
        template = SAMPLE_DATA.get(key)

        if template is not None:
            bundle = RecommendationBundle(
                accommodations=[p.model_copy(deep=True) for p in template.accommodations],
                activities=[p.model_copy(deep=True) for p in template.activities],
                restaurants=[p.model_copy(deep=True) for p in template.restaurants],
                cafes=[p.model_copy(deep=True) for p in template.cafes],
            )
        else:
            fallback = _fallback_bundle(plan.destination, plan.country)
            bundle = RecommendationBundle(
                accommodations=[p.model_copy(deep=True) for p in fallback.accommodations],
                activities=[p.model_copy(deep=True) for p in fallback.activities],
                restaurants=[p.model_copy(deep=True) for p in fallback.restaurants],
                cafes=[p.model_copy(deep=True) for p in fallback.cafes],
            )
            bundle.warnings.append(
                "선택한 목적지에 대한 세부 데이터가 부족하여 기본 추천을 제공합니다."
            )

        if "food" in preferences.interests:
            bundle.restaurants = sorted(
                bundle.restaurants,
                key=lambda p: ("food" not in (p.tags or []), -(p.rating or 0)),
            )

        await self._augment_with_google(bundle, plan, preferences)
        if not bundle.activities:
            bundle.warnings.append("활동 추천을 찾지 못했습니다. 선호도를 조정해 보세요.")
        return bundle
