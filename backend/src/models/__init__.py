"""
SQLAlchemy models for AI TravelTailor
"""

from .user import User
from .user_preference import UserPreference
from .travel_plan import TravelPlan
from .daily_itinerary import DailyItinerary
from .place import Place
from .itinerary_place import ItineraryPlace
from .route import Route
from .flight_option import FlightOption
from .accommodation_option import AccommodationOption

__all__ = [
    "User",
    "UserPreference",
    "TravelPlan",
    "DailyItinerary",
    "Place",
    "ItineraryPlace",
    "Route",
    "FlightOption",
    "AccommodationOption",
]
