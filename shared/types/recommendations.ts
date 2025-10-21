export interface FlightOption {
  id: string;
  provider: string;
  carrier: string;
  flight_number: string;
  departure_airport: string;
  arrival_airport: string;
  departure_time: string;
  arrival_time: string;
  duration_minutes: number;
  stops: number;
  seat_class?: string | null;
  baggage_info?: Record<string, unknown> | null;
  price_currency: string;
  price_amount: number;
  booking_url: string;
  created_at: string;
  updated_at: string;
}

export interface FlightRecommendations {
  plan_id: string;
  origin_airport: string;
  destination_airport: string;
  options: FlightOption[];
}

export interface AccommodationOption {
  id: string;
  provider: string;
  name: string;
  description?: string | null;
  address?: string | null;
  city?: string | null;
  country?: string | null;
  rating?: number | null;
  review_count?: number | null;
  star_rating?: number | null;
  price_currency: string;
  price_per_night?: number | null;
  total_price: number;
  check_in_date?: string | null;
  check_out_date?: string | null;
  nights?: number | null;
  room_type?: string | null;
  booking_url: string;
  image_url?: string | null;
  amenities?: string[] | null;
  tags?: string[] | null;
  created_at: string;
  updated_at: string;
}

export interface AccommodationRecommendations {
  plan_id: string;
  check_in?: string | null;
  check_out?: string | null;
  options: AccommodationOption[];
}
