/**
 * API Client for Task-Tracker Backend
 */

import type {
  ActivityLog,
  DateRangeSummary,
  StatsResponse,
  SummaryStats,
  Config,
} from '@/types/activity';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class APIError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public response?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}

async function fetchAPI<T>(endpoint: string): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
      },
      cache: 'no-store', // Always fetch fresh data
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new APIError(
        errorData.detail || `API request failed: ${response.statusText}`,
        response.status,
        errorData
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }

    // Network or parsing error
    throw new APIError(
      `Network error: ${error instanceof Error ? error.message : 'Unknown error'}`,
      undefined,
      error
    );
  }
}

export const api = {
  // Activity Data
  getTodayActivity: () => fetchAPI<ActivityLog>('/api/activity/today'),

  getDateActivity: (date: string) =>
    fetchAPI<ActivityLog>(`/api/activity/date/${date}`),

  getWeekActivity: () => fetchAPI<DateRangeSummary>('/api/activity/week'),

  getMonthActivity: () => fetchAPI<DateRangeSummary>('/api/activity/month'),

  getYearActivity: () => fetchAPI<DateRangeSummary>('/api/activity/year'),

  getRangeActivity: (start: string, end: string) =>
    fetchAPI<DateRangeSummary>(`/api/activity/range?start=${start}&end=${end}`),

  // Statistics
  getTodayStats: () => fetchAPI<StatsResponse>('/api/stats/today'),

  getWeekStats: () => fetchAPI<SummaryStats>('/api/stats/week'),

  getMonthStats: () => fetchAPI<SummaryStats>('/api/stats/month'),

  getYearStats: () => fetchAPI<SummaryStats>('/api/stats/year'),

  // Screenshots
  getTodayScreenshots: () =>
    fetchAPI<{ date: string; screenshots: any[] }>('/api/screenshots/today'),

  getDateScreenshots: (date: string) =>
    fetchAPI<{ date: string; screenshots: any[] }>(`/api/screenshots/${date}`),

  // Idle Periods
  getTodayIdlePeriods: () =>
    fetchAPI<{ date: string; idle_periods: any[] }>('/api/idle-periods/today'),

  getDateIdlePeriods: (date: string) =>
    fetchAPI<{ date: string; idle_periods: any[] }>(`/api/idle-periods/${date}`),

  // Configuration
  getConfig: () => fetchAPI<Config>('/api/config'),

  // Health Check
  healthCheck: () => fetchAPI<{ status: string; timestamp: string }>('/api/health'),
};

export { APIError };
