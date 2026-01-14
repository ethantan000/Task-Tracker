'use client';

/**
 * Badge Component for status indicators
 */

import { motion } from 'framer-motion';
import { ReactNode } from 'react';
import { cn } from '@/lib/utils';
import { fadeIn } from '@/lib/animations';

export interface BadgeProps {
  variant?: 'success' | 'warning' | 'error' | 'neutral' | 'accent';
  size?: 'sm' | 'md' | 'lg';
  icon?: ReactNode;
  pulse?: boolean;
  children: ReactNode;
  className?: string;
}

export function Badge({
  variant = 'neutral',
  size = 'md',
  icon,
  pulse = false,
  children,
  className,
}: BadgeProps) {
  const baseStyles = 'inline-flex items-center gap-1.5 font-medium rounded-full';

  const variantStyles = {
    success: 'bg-success/10 text-success',
    warning: 'bg-warning/10 text-warning',
    error: 'bg-error/10 text-error',
    neutral: 'bg-text-secondary/10 text-text-secondary',
    accent: 'bg-accent/10 text-accent',
  };

  const sizeStyles = {
    sm: 'px-2 py-0.5 text-caption-1',
    md: 'px-3 py-1 text-footnote',
    lg: 'px-4 py-1.5 text-subhead',
  };

  return (
    <motion.div
      className={cn(baseStyles, variantStyles[variant], sizeStyles[size], className)}
      variants={fadeIn}
      initial="hidden"
      animate="visible"
    >
      {icon && (
        <span className={cn('flex items-center', pulse && 'animate-pulse-glow')}>{icon}</span>
      )}
      {children}
    </motion.div>
  );
}

export function StatusDot({ variant = 'neutral', pulse = false }: Pick<BadgeProps, 'variant' | 'pulse'>) {
  const colorStyles = {
    success: 'bg-success',
    warning: 'bg-warning',
    error: 'bg-error',
    neutral: 'bg-text-secondary',
    accent: 'bg-accent',
  };

  return (
    <span
      className={cn(
        'inline-block w-2 h-2 rounded-full',
        colorStyles[variant],
        pulse && 'animate-pulse-glow'
      )}
    />
  );
}
