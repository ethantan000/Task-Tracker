/**
 * Utility functions for Task-Tracker Dashboard
 */

import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { format, parseISO, formatDistanceToNow } from 'date-fns';

/**
 * Merge Tailwind CSS classes with proper precedence
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Format seconds into human-readable time string
 */
export function formatTime(seconds: number): string {
  if (seconds < 60) {
    return `${seconds}s`;
  } else if (seconds < 3600) {
    const minutes = Math.floor(seconds / 60);
    return `${minutes}m`;
  } else {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (minutes > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${hours}h`;
  }
}

/**
 * Format seconds into detailed time string (includes seconds)
 */
export function formatTimeDetailed(seconds: number): string {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;

  const parts: string[] = [];
  if (hours > 0) parts.push(`${hours}h`);
  if (minutes > 0) parts.push(`${minutes}m`);
  if (secs > 0 || parts.length === 0) parts.push(`${secs}s`);

  return parts.join(' ');
}

/**
 * Format ISO timestamp to readable date
 */
export function formatDate(isoString: string, formatStr: string = 'MMM d, yyyy'): string {
  try {
    return format(parseISO(isoString), formatStr);
  } catch {
    return isoString;
  }
}

/**
 * Format ISO timestamp to time only
 */
export function formatTimeOnly(isoString: string): string {
  try {
    return format(parseISO(isoString), 'h:mm a');
  } catch {
    return isoString;
  }
}

/**
 * Get relative time (e.g., "2 hours ago")
 */
export function formatRelativeTime(isoString: string): string {
  try {
    return formatDistanceToNow(parseISO(isoString), { addSuffix: true });
  } catch {
    return isoString;
  }
}

/**
 * Calculate percentage
 */
export function calculatePercentage(value: number, total: number): number {
  if (total === 0) return 0;
  return Math.round((value / total) * 100);
}

/**
 * Check if currently within office hours
 */
export function isWithinOfficeHours(
  startTime: string = '09:00',
  endTime: string = '17:00'
): boolean {
  const now = new Date();
  const [startHour, startMinute] = startTime.split(':').map(Number);
  const [endHour, endMinute] = endTime.split(':').map(Number);

  const currentMinutes = now.getHours() * 60 + now.getMinutes();
  const startMinutes = startHour * 60 + startMinute;
  const endMinutes = endHour * 60 + endMinute;

  return currentMinutes >= startMinutes && currentMinutes <= endMinutes;
}

/**
 * Get status color based on activity type
 */
export function getStatusColor(type: 'work' | 'idle' | 'suspicious' | 'active'): string {
  switch (type) {
    case 'work':
    case 'active':
      return 'text-success';
    case 'idle':
      return 'text-error';
    case 'suspicious':
      return 'text-warning';
    default:
      return 'text-text-secondary';
  }
}

/**
 * Get background color based on activity type
 */
export function getBackgroundColor(type: 'work' | 'idle' | 'suspicious' | 'active'): string {
  switch (type) {
    case 'work':
    case 'active':
      return 'bg-success/10';
    case 'idle':
      return 'bg-error/10';
    case 'suspicious':
      return 'bg-warning/10';
    default:
      return 'bg-text-secondary/10';
  }
}

/**
 * Truncate text with ellipsis
 */
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
}

/**
 * Debounce function
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;

  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };

    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * Throttle function
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;

  return function executedFunction(...args: Parameters<T>) {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}

/**
 * Generate staggered animation delays for list items
 */
export function getStaggerDelay(index: number, baseDelay: number = 0.05): number {
  return index * baseDelay;
}

/**
 * Animate number counting (for use with useState)
 */
export function animateCount(
  start: number,
  end: number,
  duration: number,
  onUpdate: (value: number) => void
) {
  const startTime = Date.now();
  const endTime = startTime + duration;

  const update = () => {
    const now = Date.now();
    const progress = Math.min((now - startTime) / duration, 1);

    // Easing function (ease-out)
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = Math.round(start + (end - start) * eased);

    onUpdate(current);

    if (progress < 1) {
      requestAnimationFrame(update);
    }
  };

  requestAnimationFrame(update);
}

/**
 * Format large numbers with K/M suffixes
 */
export function formatNumber(num: number): string {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M';
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K';
  }
  return num.toString();
}

/**
 * Get day of week name
 */
export function getDayName(dateString: string): string {
  try {
    return format(parseISO(dateString), 'EEEE');
  } catch {
    return '';
  }
}

/**
 * Get month name
 */
export function getMonthName(dateString: string): string {
  try {
    return format(parseISO(dateString), 'MMMM');
  } catch {
    return '';
  }
}

/**
 * Check if date is today
 */
export function isToday(dateString: string): boolean {
  const today = format(new Date(), 'yyyy-MM-dd');
  return dateString === today;
}

/**
 * Safe JSON parse
 */
export function safeJSONParse<T>(json: string, fallback: T): T {
  try {
    return JSON.parse(json);
  } catch {
    return fallback;
  }
}
