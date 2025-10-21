import { Coordinates } from './common';
import { PlanStatus, PlaceCategory, TransportMode, TravelerType, VisitType } from './enums';

export interface TravelPreferences {
  interests: string[];
  must_have: string[];
  avoid: string[];
  dietary_restrictions: string[];
  pace: 'slow' | 'normal' | 'fast';
  notes?: string;
}

export interface TravelPlanCreate {
  title?: string;
  destination: string;
  country: string;
  start_date: string;
  end_date: string;
  budget_total: number;
  traveler_type: TravelerType;
  traveler_count: number;
  preferences: TravelPreferences;
}

export interface BudgetBreakdown {
  accommodation: number;
  food: number;
  activities: number;
  transport: number;
}

export interface PlaceBase extends Coordinates {
  id: string;
  name: string;
  category: PlaceCategory;
  address?: string;
  city?: string;
  country?: string;
  rating?: number;
  price_level?: number;
  photos?: string[];
  description?: string;
}

export interface ItineraryPlace extends PlaceBase {
  place_id: string;
  visit_order: number;
  visit_type: VisitType;
  visit_time?: string;
  duration_minutes?: number;
  estimated_cost?: number;
  ai_recommendation_reason?: string;
  user_notes?: string;
  is_confirmed: boolean;
}

export interface RouteSegment {
  id: string;
  daily_itinerary_id: string;
  from_place_id: string;
  to_place_id: string;
  from_order: number;
  to_order: number;
  transport_mode: TransportMode;
  distance_meters?: number;
  duration_minutes?: number;
  estimated_cost?: number;
  route_polyline?: string;
  instructions?: Record<string, unknown> | null;
}

export interface DailyItinerary {
  id: string;
  travel_plan_id: string;
  date: string;
  day_number: number;
  theme?: string;
  notes?: string;
  weather_forecast?: Record<string, unknown> | null;
  places: ItineraryPlace[];
  routes: RouteSegment[];
}

export interface TravelPlanSummary {
  id: string;
  title: string;
  destination: string;
  start_date: string;
  end_date: string;
  total_days: number;
  total_nights: number;
  status: PlanStatus;
  budget_total: number;
  created_at: string;
}

export interface TravelPlanDetail {
  id: string;
  user_id: string;
  title: string;
  destination: string;
  country: string;
  start_date: string;
  end_date: string;
  total_days: number;
  total_nights: number;
  budget_total: number;
  budget_allocated?: number;
  budget_breakdown?: BudgetBreakdown;
  traveler_type: TravelerType;
  traveler_count: number;
  preferences: Record<string, unknown>;
  status: PlanStatus;
  ai_model_version?: string;
  generation_time_seconds?: number;
  created_at: string;
  updated_at: string;
  daily_itineraries: DailyItinerary[];
}

export interface TravelPlanStatus {
  id: string;
  status: PlanStatus;
  progress: number;
  message?: string;
}

export interface TravelPlanUpdate {
  title?: string;
  status?: PlanStatus;
  preferences?: Record<string, unknown>;
}
