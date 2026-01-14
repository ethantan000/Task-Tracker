'use client';

/**
 * Main Dashboard Page - Apple-inspired Task Tracker
 */

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Typography } from '@/components/atoms/Typography';
import { Badge, StatusDot } from '@/components/atoms/Badge';
import { StatCard } from '@/components/molecules/StatCard';
import { TabNavigation } from '@/components/molecules/TabNavigation';
import { StatCardSkeleton } from '@/components/atoms/Skeleton';
import { useActivityData, useConfig, useRealtime } from '@/hooks/useActivityData';
import { formatTime, formatDate, isWithinOfficeHours } from '@/lib/utils';
import { pageTransition, staggerContainer, staggerItem } from '@/lib/animations';
import type { ViewPeriod } from '@/types/activity';

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState<ViewPeriod>('daily');

  // Fetch data based on active tab
  const { data: activityData, isLoading, error } = useActivityData(activeTab);
  const { data: config } = useConfig();

  // Enable real-time updates
  useRealtime();

  // Check if currently within office hours
  const isActive = isWithinOfficeHours(
    config?.office_hours.start,
    config?.office_hours.end
  );

  const tabs = [
    { id: 'daily', label: 'Daily', icon: '📅' },
    { id: 'weekly', label: 'Weekly', icon: '📊' },
    { id: 'monthly', label: 'Monthly', icon: '📈' },
    { id: 'yearly', label: 'Yearly', icon: '🗓️' },
  ];

  // Render stats based on period
  const renderStats = () => {
    if (isLoading) {
      return (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <StatCardSkeleton key={i} />
          ))}
        </div>
      );
    }

    if (error) {
      return (
        <div className="glass-card p-8 text-center">
          <Typography variant="headline" color="error">
            Failed to load dashboard data
          </Typography>
          <Typography variant="body" color="secondary" className="mt-2">
            {error instanceof Error ? error.message : 'Unknown error occurred'}
          </Typography>
        </div>
      );
    }

    if (!activityData) return null;

    // Daily view
    if (activeTab === 'daily' && 'work_seconds' in activityData) {
      const workSeconds = activityData.work_seconds || 0;
      const idleSeconds = activityData.idle_seconds || 0;
      const suspiciousSeconds = activityData.suspicious_seconds || 0;
      const realWorkSeconds = workSeconds - suspiciousSeconds;
      const screenshotCount = activityData.screenshots?.length || 0;
      const keyboardCount = activityData.keyboard_activity_count || 0;
      const windowCount = activityData.window_change_count || 0;

      return (
        <motion.div
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6"
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
        >
          <motion.div variants={staggerItem}>
            <StatCard
              label="Work Time"
              value={formatTime(workSeconds)}
              icon="⏱️"
              color="success"
              subtitle={`${Math.round(workSeconds / 3600)}h total`}
            />
          </motion.div>

          <motion.div variants={staggerItem}>
            <StatCard
              label="Real Work"
              value={formatTime(realWorkSeconds)}
              icon="✅"
              color="accent"
              subtitle="Verified activity"
            />
          </motion.div>

          <motion.div variants={staggerItem}>
            <StatCard
              label="Idle Time"
              value={formatTime(idleSeconds)}
              icon="⏸️"
              color="error"
              subtitle={`${activityData.idle_periods?.length || 0} breaks`}
            />
          </motion.div>

          <motion.div variants={staggerItem}>
            <StatCard
              label="Suspicious"
              value={formatTime(suspiciousSeconds)}
              icon="⚠️"
              color="warning"
              subtitle="Flagged activity"
            />
          </motion.div>

          <motion.div variants={staggerItem}>
            <StatCard
              label="Screenshots"
              value={screenshotCount}
              icon="📸"
              color="neutral"
              subtitle={`Every ${config?.screenshot_interval || 180}s`}
            />
          </motion.div>

          <motion.div variants={staggerItem}>
            <StatCard
              label="Keystrokes"
              value={keyboardCount.toLocaleString()}
              icon="⌨️"
              color="neutral"
              subtitle="Total presses"
            />
          </motion.div>

          <motion.div variants={staggerItem}>
            <StatCard
              label="Window Switches"
              value={windowCount}
              icon="🪟"
              color="neutral"
              subtitle="App changes"
            />
          </motion.div>

          <motion.div variants={staggerItem}>
            <StatCard
              label="Status"
              value={isActive ? 'Active' : 'Off Hours'}
              icon={isActive ? '🟢' : '🔴'}
              color={isActive ? 'success' : 'error'}
              subtitle={`${config?.office_hours.start || '09:00'} - ${config?.office_hours.end || '17:00'}`}
            />
          </motion.div>
        </motion.div>
      );
    }

    // Summary view (weekly, monthly, yearly)
    if ('total_work_seconds' in activityData) {
      const totalWork = activityData.total_work_seconds || 0;
      const totalIdle = activityData.total_idle_seconds || 0;
      const totalSuspicious = activityData.total_suspicious_seconds || 0;
      const totalRealWork = totalWork - totalSuspicious;
      const avgWorkPerDay = activityData.average_work_per_day || 0;
      const totalScreenshots = activityData.total_screenshot_count || 0;
      const daysCount = activityData.daily_breakdown?.length || 0;

      return (
        <motion.div
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6"
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
        >
          <motion.div variants={staggerItem}>
            <StatCard
              label="Total Work"
              value={formatTime(totalWork)}
              icon="⏱️"
              color="success"
              subtitle={`${daysCount} days tracked`}
            />
          </motion.div>

          <motion.div variants={staggerItem}>
            <StatCard
              label="Real Work"
              value={formatTime(totalRealWork)}
              icon="✅"
              color="accent"
              subtitle="Verified total"
            />
          </motion.div>

          <motion.div variants={staggerItem}>
            <StatCard
              label="Avg Per Day"
              value={formatTime(Math.round(avgWorkPerDay))}
              icon="📊"
              color="neutral"
              subtitle="Daily average"
            />
          </motion.div>

          <motion.div variants={staggerItem}>
            <StatCard
              label="Total Idle"
              value={formatTime(totalIdle)}
              icon="⏸️"
              color="error"
              subtitle="Break time"
            />
          </motion.div>

          <motion.div variants={staggerItem}>
            <StatCard
              label="Suspicious"
              value={formatTime(totalSuspicious)}
              icon="⚠️"
              color="warning"
              subtitle="Flagged total"
            />
          </motion.div>

          <motion.div variants={staggerItem}>
            <StatCard
              label="Screenshots"
              value={totalScreenshots}
              icon="📸"
              color="neutral"
              subtitle="Total captured"
            />
          </motion.div>

          <motion.div variants={staggerItem}>
            <StatCard
              label="Productivity"
              value={`${Math.round((totalRealWork / (totalWork || 1)) * 100)}%`}
              icon="🎯"
              color="accent"
              subtitle="Real work ratio"
            />
          </motion.div>

          <motion.div variants={staggerItem}>
            <StatCard
              label="Status"
              value={isActive ? 'Active' : 'Off Hours'}
              icon={isActive ? '🟢' : '🔴'}
              color={isActive ? 'success' : 'error'}
              subtitle={`${config?.office_hours.start || '09:00'} - ${config?.office_hours.end || '17:00'}`}
            />
          </motion.div>
        </motion.div>
      );
    }

    return null;
  };

  return (
    <motion.div
      className="min-h-screen bg-background-primary p-4 sm:p-6 lg:p-8"
      variants={pageTransition}
      initial="initial"
      animate="animate"
    >
      <div className="max-w-[2000px] mx-auto space-y-8">
        {/* Header */}
        <motion.div
          className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <div>
            <Typography variant="display" weight="bold" className="mb-2">
              Task Tracker
            </Typography>
            <div className="flex items-center gap-3">
              <Badge variant={isActive ? 'success' : 'neutral'} icon={<StatusDot variant={isActive ? 'success' : 'neutral'} pulse={isActive} />}>
                {isActive ? 'Currently Active' : 'Off Hours'}
              </Badge>
              <Typography variant="subhead" color="secondary">
                {formatDate(new Date().toISOString(), 'EEEE, MMMM d, yyyy')}
              </Typography>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Typography variant="caption-1" color="tertiary" className="hidden sm:block">
              Updates every 30s
            </Typography>
          </div>
        </motion.div>

        {/* Tab Navigation */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <TabNavigation
            tabs={tabs}
            activeTab={activeTab}
            onChange={(tab) => setActiveTab(tab as ViewPeriod)}
          />
        </motion.div>

        {/* Stats Grid */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            {renderStats()}
          </motion.div>
        </AnimatePresence>

        {/* Additional Info */}
        {activityData && 'daily_breakdown' in activityData && (
          <motion.div
            className="glass-card p-6"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
          >
            <Typography variant="headline" weight="semibold" className="mb-4">
              Daily Breakdown
            </Typography>
            <div className="space-y-3">
              {activityData.daily_breakdown.slice(0, 7).map((day, index) => (
                <motion.div
                  key={day.date}
                  className="flex items-center justify-between p-4 bg-white/30 rounded-apple-lg"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.5 + index * 0.05 }}
                >
                  <div className="flex-1">
                    <Typography variant="callout" weight="semibold">
                      {formatDate(day.date, 'EEE, MMM d')}
                    </Typography>
                    <Typography variant="caption-1" color="secondary">
                      {formatTime(day.work_seconds)} work • {formatTime(day.idle_seconds)} idle
                    </Typography>
                  </div>
                  <div className="text-right">
                    <Typography variant="headline" color="accent" weight="semibold">
                      {formatTime(day.real_work_seconds)}
                    </Typography>
                    <Typography variant="caption-1" color="tertiary">
                      real work
                    </Typography>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Footer */}
        <motion.div
          className="text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
        >
          <Typography variant="caption-1" color="tertiary">
            Task-Tracker v2.0 • Real-time Activity Monitoring
          </Typography>
        </motion.div>
      </div>
    </motion.div>
  );
}
