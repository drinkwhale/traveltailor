/**
 * Common utility types
 */

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface Coordinates {
  latitude: number;
  longitude: number;
}

export interface DateRange {
  start_date: string;
  end_date: string;
}
