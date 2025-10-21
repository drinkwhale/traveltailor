"""
Recommendation service package
"""

from .flight_recommender import FlightRecommender, FlightRecommendationResult
from .accommodation_recommender import (
    AccommodationRecommender,
    AccommodationRecommendationResult,
)

__all__ = [
    "FlightRecommender",
    "FlightRecommendationResult",
    "AccommodationRecommender",
    "AccommodationRecommendationResult",
]
