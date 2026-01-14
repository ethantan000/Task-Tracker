'use client';

/**
 * Glassmorphic Button Component (Apple-style)
 */

import { motion, HTMLMotionProps } from 'framer-motion';
import { ReactNode, forwardRef } from 'react';
import { cn } from '@/lib/utils';
import { springs } from '@/lib/animations';

export interface ButtonProps extends Omit<HTMLMotionProps<'button'>, 'ref'> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  icon?: ReactNode;
  iconPosition?: 'left' | 'right';
  loading?: boolean;
  fullWidth?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      icon,
      iconPosition = 'left',
      loading = false,
      fullWidth = false,
      children,
      className,
      disabled,
      ...props
    },
    ref
  ) => {
    const baseStyles = 'inline-flex items-center justify-center gap-2 font-semibold transition-all focus-ring';

    const variantStyles = {
      primary: 'glass-card hover:bg-white/90 text-text-primary active:bg-white/70',
      secondary: 'bg-background-tertiary hover:bg-white text-text-primary active:bg-background-secondary',
      ghost: 'bg-transparent hover:bg-white/30 text-text-primary active:bg-white/20',
      danger: 'bg-error/10 hover:bg-error/20 text-error active:bg-error/30',
    };

    const sizeStyles = {
      sm: 'px-4 py-2 text-subhead rounded-apple',
      md: 'px-6 py-3 text-headline rounded-apple-lg',
      lg: 'px-8 py-4 text-title-3 rounded-apple-xl',
    };

    const disabledStyles = 'opacity-40 cursor-not-allowed pointer-events-none';

    return (
      <motion.button
        ref={ref}
        className={cn(
          baseStyles,
          variantStyles[variant],
          sizeStyles[size],
          fullWidth && 'w-full',
          (disabled || loading) && disabledStyles,
          className
        )}
        whileHover={!disabled && !loading ? { y: -2, scale: 1.02 } : undefined}
        whileTap={!disabled && !loading ? { scale: 0.98 } : undefined}
        transition={springs.snappy}
        disabled={disabled || loading}
        {...props}
      >
        {loading && (
          <motion.div
            className="w-4 h-4 border-2 border-current border-t-transparent rounded-full"
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          />
        )}

        {!loading && icon && iconPosition === 'left' && <span>{icon}</span>}

        {children}

        {!loading && icon && iconPosition === 'right' && <span>{icon}</span>}
      </motion.button>
    );
  }
);

Button.displayName = 'Button';
