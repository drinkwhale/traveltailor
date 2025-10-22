export interface UserPreferenceResponse {
  default_budget_min: number | null;
  default_budget_max: number | null;
  preferred_traveler_types: string[];
  preferred_interests: string[];
  avoided_activities: string[];
  dietary_restrictions: string[];
  preferred_accommodation_type: string[];
  mobility_considerations: string | null;
  preferred_pace?: string | null;
  recent_notes?: string | null;
  last_budget_total?: number | null;
  updated_at?: string | null;
}

export interface UserPreferenceUpdatePayload {
  default_budget_min: number | null;
  default_budget_max: number | null;
  preferred_traveler_types: string[];
  preferred_interests: string[];
  avoided_activities: string[];
  dietary_restrictions: string[];
  preferred_accommodation_type: string[];
  mobility_considerations: string | null;
}

export const emptyPreferenceResponse: UserPreferenceResponse = {
  default_budget_min: null,
  default_budget_max: null,
  preferred_traveler_types: [],
  preferred_interests: [],
  avoided_activities: [],
  dietary_restrictions: [],
  preferred_accommodation_type: [],
  mobility_considerations: null,
  preferred_pace: null,
  recent_notes: null,
  last_budget_total: null,
  updated_at: null,
}
