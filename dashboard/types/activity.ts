/**
 * Type definitions for Task-Tracker activity data
 */

export interface Screenshot {
  time: string; // ISO timestamp
  path: string;
  url?: string; // API endpoint URL
  suspicious: boolean;
}

export interface IdlePeriod {
  left: string; // ISO timestamp
  returned: string; // ISO timestamp
  duration_seconds: number;
}

export interface SuspiciousEvent {
  time: string; // ISO timestamp
  duration: number;
  reason: string;
}

export interface Session {
  start: string; // ISO timestamp
  end: string; // ISO timestamp
  duration_seconds: number;
}

export interface ActivityLog {
  date: string; // YYYY-MM-DD
  work_seconds: number;
  idle_seconds: number;
  overtime_seconds: number;
  suspicious_seconds: number;
  real_work_seconds?: number; // Computed: work - suspicious
  screenshot_count?: number; // Computed: screenshots.length
  screenshots: Screenshot[];
  sessions: Session[];
  current_session_start: string | null;
  suspicious_events: SuspiciousEvent[];
  keyboard_activity_count: number;
  window_change_count: number;
  idle_periods: IdlePeriod[];
  current_idle_start: string | null;
}

export interface DailyBreakdown {
  date: string;
  work_seconds: number;
  idle_seconds: number;
  overtime_seconds: number;
  suspicious_seconds: number;
  real_work_seconds: number;
  screenshot_count: number;
  keyboard_activity_count: number;
  window_change_count: number;
}

export interface DateRangeSummary {
  start_date: string;
  end_date: string;
  total_work_seconds: number;
  total_idle_seconds: number;
  total_overtime_seconds: number;
  total_suspicious_seconds: number;
  total_real_work_seconds: number;
  total_screenshot_count: number;
  total_keyboard_activity: number;
  total_window_changes: number;
  average_work_per_day: number;
  average_idle_per_day: number;
  daily_breakdown: DailyBreakdown[];
}

export interface FormattedTime {
  seconds: number;
  formatted: string; // e.g., "5h 7m"
}

export interface StatValue {
  work_time: FormattedTime;
  idle_time: FormattedTime;
  suspicious_time: FormattedTime;
  real_work_time: FormattedTime;
  keyboard_activity: number;
  window_changes: number;
  screenshot_count: number;
  idle_period_count: number;
}

export interface StatsResponse {
  date: string;
  stats: StatValue;
}

export interface SummaryStats {
  period: 'week' | 'month' | 'year';
  start_date: string;
  end_date: string;
  totals: {
    work_time: FormattedTime;
    idle_time: FormattedTime;
    suspicious_time: FormattedTime;
    real_work_time: FormattedTime;
    screenshot_count: number;
    keyboard_activity: number;
    window_changes: number;
  };
  averages: {
    work_per_day: FormattedTime;
    idle_per_day: FormattedTime;
  };
  daily_breakdown: DailyBreakdown[];
}

export interface Config {
  office_hours: {
    start: string; // HH:MM
    end: string; // HH:MM
  };
  screenshot_interval: number; // seconds
  idle_timeout: number; // seconds
  anti_cheat_enabled: boolean;
}

export interface WebSocketMessage {
  type: 'activity_update' | 'pong';
  timestamp: string;
}

// UI State Types
export type ViewPeriod = 'daily' | 'weekly' | 'monthly' | 'yearly';

export interface ChartDataPoint {
  label: string;
  work: number;
  idle: number;
  suspicious: number;
}
