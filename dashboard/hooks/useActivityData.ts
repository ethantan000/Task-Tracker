/**
 * Custom hooks for fetching activity data
 */

import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useEffect } from 'react';
import { api } from '@/lib/api';
import type { ViewPeriod } from '@/types/activity';

export function useActivityData(period: ViewPeriod) {
  const queryKey = ['activity', period];

  return useQuery({
    queryKey,
    queryFn: () => {
      switch (period) {
        case 'daily':
          return api.getTodayActivity();
        case 'weekly':
          return api.getWeekActivity();
        case 'monthly':
          return api.getMonthActivity();
        case 'yearly':
          return api.getYearActivity();
        default:
          return api.getTodayActivity();
      }
    },
  });
}

export function useTodayActivity() {
  return useQuery({
    queryKey: ['activity', 'today'],
    queryFn: api.getTodayActivity,
  });
}

export function useDateActivity(date: string) {
  return useQuery({
    queryKey: ['activity', 'date', date],
    queryFn: () => api.getDateActivity(date),
    enabled: !!date,
  });
}

export function useWeekActivity() {
  return useQuery({
    queryKey: ['activity', 'week'],
    queryFn: api.getWeekActivity,
  });
}

export function useMonthActivity() {
  return useQuery({
    queryKey: ['activity', 'month'],
    queryFn: api.getMonthActivity,
  });
}

export function useYearActivity() {
  return useQuery({
    queryKey: ['activity', 'year'],
    queryFn: api.getYearActivity,
  });
}

export function useStats(period: ViewPeriod) {
  const queryKey = ['stats', period];

  return useQuery({
    queryKey,
    queryFn: () => {
      switch (period) {
        case 'daily':
          return api.getTodayStats();
        case 'weekly':
          return api.getWeekStats();
        case 'monthly':
          return api.getMonthStats();
        case 'yearly':
          return api.getYearStats();
        default:
          return api.getTodayStats();
      }
    },
  });
}

export function useScreenshots(date?: string) {
  return useQuery({
    queryKey: ['screenshots', date || 'today'],
    queryFn: () => (date ? api.getDateScreenshots(date) : api.getTodayScreenshots()),
  });
}

export function useIdlePeriods(date?: string) {
  return useQuery({
    queryKey: ['idle-periods', date || 'today'],
    queryFn: () => (date ? api.getDateIdlePeriods(date) : api.getTodayIdlePeriods()),
  });
}

export function useConfig() {
  return useQuery({
    queryKey: ['config'],
    queryFn: api.getConfig,
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: false, // Don't auto-refetch config
  });
}

/**
 * Hook for real-time updates via WebSocket
 */
export function useRealtime() {
  const queryClient = useQueryClient();

  useEffect(() => {
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws/activity';
    let ws: WebSocket | null = null;
    let reconnectTimeout: NodeJS.Timeout;

    const connect = () => {
      try {
        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
          console.log('✅ WebSocket connected');
        };

        ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);

            if (message.type === 'activity_update') {
              console.log('🔄 Activity update received');
              // Invalidate all activity queries to trigger refetch
              queryClient.invalidateQueries({ queryKey: ['activity'] });
              queryClient.invalidateQueries({ queryKey: ['stats'] });
              queryClient.invalidateQueries({ queryKey: ['screenshots'] });
              queryClient.invalidateQueries({ queryKey: ['idle-periods'] });
            } else if (message.type === 'pong') {
              // Heartbeat response
              console.log('💓 Heartbeat');
            }
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };

        ws.onerror = (error) => {
          console.error('❌ WebSocket error:', error);
        };

        ws.onclose = () => {
          console.log('🔌 WebSocket disconnected. Reconnecting in 5s...');
          reconnectTimeout = setTimeout(connect, 5000);
        };
      } catch (error) {
        console.error('Failed to connect WebSocket:', error);
        reconnectTimeout = setTimeout(connect, 5000);
      }
    };

    connect();

    // Send heartbeat every 30 seconds
    const heartbeat = setInterval(() => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'ping' }));
      }
    }, 30000);

    return () => {
      clearInterval(heartbeat);
      clearTimeout(reconnectTimeout);
      if (ws) {
        ws.close();
      }
    };
  }, [queryClient]);
}
