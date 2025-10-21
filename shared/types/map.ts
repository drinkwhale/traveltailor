import type { TransportMode } from './enums';

export interface MapCoordinate {
  latitude: number;
  longitude: number;
}

export interface MapBounds {
  southwest: MapCoordinate;
  northeast: MapCoordinate;
}

export interface MapMarker {
  id: string;
  place_id: string;
  name: string;
  order: number;
  latitude: number;
  longitude: number;
  category: string;
  visit_time?: string;
  address?: string;
}

export interface MapRouteStep {
  instruction: string;
  distance_meters: number;
  duration_seconds: number;
}

export interface MapRoute {
  id: string;
  from_place_id: string;
  to_place_id: string;
  from_order: number;
  to_order: number;
  transport_mode: TransportMode;
  distance_meters?: number;
  duration_minutes?: number;
  polyline: string;
  summary?: string | null;
  steps: MapRouteStep[];
}

export interface MapDaySummary {
  total_distance_meters: number;
  total_duration_minutes: number;
}

export interface MapLink {
  web: string;
  mobile?: string | null;
}

export interface MapExportLinks {
  google_maps: MapLink;
  kakao_map: MapLink;
}

export interface MapDay {
  day_number: number;
  date: string;
  theme?: string | null;
  markers: MapMarker[];
  routes: MapRoute[];
  summary: MapDaySummary;
  export_links: MapExportLinks;
}

export interface MapExportPlan {
  id: string;
  title: string;
  destination: string;
  start_date: string;
  end_date: string;
}

export interface MapExportResponse {
  plan: MapExportPlan;
  bounds: MapBounds;
  days: MapDay[];
}
