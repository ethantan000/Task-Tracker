'use client';

/**
 * Glassmorphic Stat Card Component (Apple-style)
 */

import { motion } from 'framer-motion';
import { ReactNode } from 'react';
import { cn } from '@/lib/utils';
import { Typography } from '@/components/atoms/Typography';
import { Badge } from '@/components/atoms/Badge';
import { fadeIn, hoverLift } from '@/lib/animations';

export interface StatCardProps {
  label: string;
  value: string | number;
  icon?: ReactNode;
  trend?: {
    value: number;
    direction: 'up' | 'down';
  };
  color?: 'success' | 'warning' | 'error' | 'accent' | 'neutral';
  subtitle?: string;
  loading?: boolean;
  className?: string;
  onClick?: () => void;
}

const colorStyles = {
  success: 'text-success',
  warning: 'text-warning',
  error: 'text-error',
  accent: 'text-accent',
  neutral: 'text-text-primary',
};

const colorGradients = {
  success: 'from-success/20 to-success/5',
  warning: 'from-warning/20 to-warning/5',
  error: 'from-error/20 to-error/5',
  accent: 'from-accent/20 to-accent/5',
  neutral: 'from-text-secondary/10 to-transparent',
};

export function StatCard({
  label,
  value,
  icon,
  trend,
  color = 'neutral',
  subtitle,
  loading = false,
  className,
  onClick,
}: StatCardProps) {
  const isClickable = !!onClick;

  return (
    <motion.div
      className={cn(
        'glass-card p-6 relative overflow-hidden',
        isClickable && 'cursor-pointer',
        className
      )}
      variants={fadeIn}
      initial="hidden"
      animate="visible"
      whileHover={isClickable ? { y: -4, scale: 1.02 } : undefined}
      whileTap={isClickable ? { scale: 0.98 } : undefined}
      onClick={onClick}
    >
      {/* Gradient Background */}
      <div
        className={cn(
          'absolute inset-0 opacity-50 bg-gradient-to-br pointer-events-none',
          colorGradients[color]
        )}
      />

      {/* Content */}
      <div className="relative z-10">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          {/* Icon */}
          {icon && (
            <motion.div
              className={cn(
                'w-12 h-12 rounded-apple-lg flex items-center justify-center',
                'bg-white/50 backdrop-blur-sm',
                colorStyles[color]
              )}
              whileHover={{ rotate: 5, scale: 1.1 }}
              transition={{ type: 'spring', stiffness: 400, damping: 25 }}
            >
              <span className="text-2xl">{icon}</span>
            </motion.div>
          )}

          {/* Trend Badge */}
          {trend && (
            <Badge
              variant={trend.direction === 'up' ? 'success' : 'error'}
              size="sm"
              icon={
                trend.direction === 'up' ? (
                  <svg
                    className="w-3 h-3"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M5 10l7-7m0 0l7 7m-7-7v18"
                    />
                  </svg>
                ) : (
                  <svg
                    className="w-3 h-3"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 14l-7 7m0 0l-7-7m7 7V3"
                    />
                  </svg>
                )
              }
            >
              {Math.abs(trend.value)}%
            </Badge>
          )}
        </div>

        {/* Label */}
        <Typography variant="subhead" color="secondary" className="mb-2">
          {label}
        </Typography>

        {/* Value */}
        <motion.div
          key={value}
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ type: 'spring', stiffness: 500, damping: 30 }}
        >
          <Typography
            variant="title-1"
            color={color === 'neutral' ? 'primary' : (color as any)}
            weight="bold"
            className="mb-1"
          >
            {loading ? '—' : value}
          </Typography>
        </motion.div>

        {/* Subtitle */}
        {subtitle && (
          <Typography variant="caption-1" color="tertiary">
            {subtitle}
          </Typography>
        )}
      </div>

      {/* Border Accent */}
      <div
        className={cn(
          'absolute bottom-0 left-0 right-0 h-1 opacity-50',
          `bg-gradient-to-r ${colorGradients[color]}`
        )}
      />
    </motion.div>
  );
}

export function StatCardCompact({
  label,
  value,
  icon,
  color = 'neutral',
  className,
}: Pick<StatCardProps, 'label' | 'value' | 'icon' | 'color' | 'className'>) {
  return (
    <div className={cn('flex items-center gap-3 p-4 glass-card', className)}>
      {icon && (
        <div
          className={cn(
            'w-10 h-10 rounded-apple flex items-center justify-center bg-white/50',
            colorStyles[color]
          )}
        >
          {icon}
        </div>
      )}
      <div className="flex-1 min-w-0">
        <Typography variant="caption-1" color="secondary" className="truncate">
          {label}
        </Typography>
        <Typography variant="headline" color={color === 'neutral' ? 'primary' : (color as any)} weight="semibold">
          {value}
        </Typography>
      </div>
    </div>
  );
}
