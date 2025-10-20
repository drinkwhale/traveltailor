/**
 * Shared TypeScript types for AI TripSmith
 * Frontend와 Backend 간 공유되는 타입 정의
 */

// Common enums
export type TravelerType = 'couple' | 'family' | 'solo' | 'friends';
export type Interest = 'food' | 'sightseeing' | 'relaxation' | 'culture' | 'adventure' | 'shopping' | 'nightlife';
export type PlaceCategory = 'accommodation' | 'restaurant' | 'cafe' | 'attraction' | 'shopping' | 'transport';
export type TransportMode = 'walking' | 'driving' | 'public_transit' | 'taxi' | 'bicycle';
export type PlanStatus = 'draft' | 'completed' | 'archived';
export type VisitType = 'overnight' | 'meal' | 'activity' | 'transit';

// Base types
export interface User {
  id: string;
  email: string;
  full_name?: string;
  created_at: string;
  updated_at: string;
}

export interface TravelPlan {
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
  traveler_type: TravelerType;
  traveler_count: number;
  status: PlanStatus;
  created_at: string;
  updated_at: string;
}

export interface Place {
  id: string;
  name: string;
  category: PlaceCategory;
  address?: string;
  latitude: number;
  longitude: number;
  rating?: number;
  price_level?: number;
  photos?: string[];
  description?: string;
}

export interface DailyItinerary {
  id: string;
  travel_plan_id: string;
  date: string;
  day_number: number;
  theme?: string;
  notes?: string;
}

// Export all types
export * from './common';
