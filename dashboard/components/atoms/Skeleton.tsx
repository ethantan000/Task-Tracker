'use client';

/**
 * Skeleton Loading Component (Apple-style shimmer effect)
 */

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

export interface SkeletonProps {
  variant?: 'text' | 'circular' | 'rectangular' | 'statCard' | 'image';
  width?: string | number;
  height?: string | number;
  count?: number;
  className?: string;
}

export function Skeleton({
  variant = 'rectangular',
  width,
  height,
  count = 1,
  className,
}: SkeletonProps) {
  const baseStyles = 'animate-shimmer bg-background-tertiary';

  const variantStyles = {
    text: 'h-4 w-full rounded',
    circular: 'rounded-full',
    rectangular: 'rounded-apple',
    statCard: 'h-32 w-full rounded-apple-xl',
    image: 'h-48 w-full rounded-apple-lg',
  };

  const style = {
    width: width ? (typeof width === 'number' ? `${width}px` : width) : undefined,
    height: height ? (typeof height === 'number' ? `${height}px` : height) : undefined,
  };

  if (count > 1) {
    return (
      <div className="space-y-3">
        {Array.from({ length: count }).map((_, index) => (
          <motion.div
            key={index}
            className={cn(baseStyles, variantStyles[variant], className)}
            style={style}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: index * 0.05 }}
          />
        ))}
      </div>
    );
  }

  return (
    <motion.div
      className={cn(baseStyles, variantStyles[variant], className)}
      style={style}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    />
  );
}

export function StatCardSkeleton() {
  return (
    <div className="glass-card p-6 space-y-4">
      <div className="flex items-center justify-between">
        <Skeleton variant="circular" width={40} height={40} />
        <Skeleton variant="text" width={60} height={20} />
      </div>
      <div className="space-y-2">
        <Skeleton variant="text" width="40%" height={16} />
        <Skeleton variant="text" width="60%" height={32} />
      </div>
    </div>
  );
}

export function ScreenshotSkeleton() {
  return (
    <div className="glass-card p-4 space-y-3">
      <Skeleton variant="image" />
      <div className="space-y-2">
        <Skeleton variant="text" width="70%" />
        <Skeleton variant="text" width="40%" />
      </div>
    </div>
  );
}

export function DailyBreakdownSkeleton() {
  return (
    <div className="glass-card p-6 space-y-4">
      <div className="flex items-center justify-between">
        <Skeleton variant="text" width="30%" height={24} />
        <Skeleton variant="circular" width={24} height={24} />
      </div>
      <div className="grid grid-cols-3 gap-4">
        <Skeleton variant="rectangular" height={60} />
        <Skeleton variant="rectangular" height={60} />
        <Skeleton variant="rectangular" height={60} />
      </div>
    </div>
  );
}
