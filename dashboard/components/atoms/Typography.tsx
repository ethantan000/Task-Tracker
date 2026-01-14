'use client';

/**
 * Typography Component (Apple SF Pro Text/Display hierarchy)
 */

import { ReactNode, ElementType } from 'react';
import { cn } from '@/lib/utils';

export interface TypographyProps {
  variant?:
    | 'display-large'
    | 'display'
    | 'title-1'
    | 'title-2'
    | 'title-3'
    | 'headline'
    | 'body'
    | 'callout'
    | 'subhead'
    | 'footnote'
    | 'caption-1'
    | 'caption-2';
  as?: ElementType;
  color?: 'primary' | 'secondary' | 'tertiary' | 'success' | 'warning' | 'error' | 'accent';
  weight?: 'regular' | 'medium' | 'semibold' | 'bold';
  mono?: boolean;
  truncate?: boolean;
  children: ReactNode;
  className?: string;
}

const variantMapping: Record<string, ElementType> = {
  'display-large': 'h1',
  'display': 'h1',
  'title-1': 'h1',
  'title-2': 'h2',
  'title-3': 'h3',
  'headline': 'h4',
  'body': 'p',
  'callout': 'p',
  'subhead': 'p',
  'footnote': 'span',
  'caption-1': 'span',
  'caption-2': 'span',
};

const colorStyles = {
  primary: 'text-text-primary',
  secondary: 'text-text-secondary',
  tertiary: 'text-text-tertiary',
  success: 'text-success',
  warning: 'text-warning',
  error: 'text-error',
  accent: 'text-accent',
};

const weightStyles = {
  regular: 'font-normal',
  medium: 'font-medium',
  semibold: 'font-semibold',
  bold: 'font-bold',
};

export function Typography({
  variant = 'body',
  as,
  color = 'primary',
  weight,
  mono = false,
  truncate = false,
  children,
  className,
}: TypographyProps) {
  const Component = as || variantMapping[variant] || 'p';

  // Determine default font family based on variant
  const fontFamily = mono ? 'font-mono' : variant.includes('display') ? 'font-display' : 'font-text';

  return (
    <Component
      className={cn(
        `text-${variant}`,
        fontFamily,
        colorStyles[color],
        weight && weightStyles[weight],
        truncate && 'truncate',
        className
      )}
    >
      {children}
    </Component>
  );
}

// Convenience components
export function DisplayLarge({ children, className, ...props }: Omit<TypographyProps, 'variant'>) {
  return (
    <Typography variant="display-large" className={className} {...props}>
      {children}
    </Typography>
  );
}

export function Display({ children, className, ...props }: Omit<TypographyProps, 'variant'>) {
  return (
    <Typography variant="display" className={className} {...props}>
      {children}
    </Typography>
  );
}

export function Title1({ children, className, ...props }: Omit<TypographyProps, 'variant'>) {
  return (
    <Typography variant="title-1" className={className} {...props}>
      {children}
    </Typography>
  );
}

export function Title2({ children, className, ...props }: Omit<TypographyProps, 'variant'>) {
  return (
    <Typography variant="title-2" className={className} {...props}>
      {children}
    </Typography>
  );
}

export function Title3({ children, className, ...props }: Omit<TypographyProps, 'variant'>) {
  return (
    <Typography variant="title-3" className={className} {...props}>
      {children}
    </Typography>
  );
}

export function Headline({ children, className, ...props }: Omit<TypographyProps, 'variant'>) {
  return (
    <Typography variant="headline" className={className} {...props}>
      {children}
    </Typography>
  );
}

export function Body({ children, className, ...props }: Omit<TypographyProps, 'variant'>) {
  return (
    <Typography variant="body" className={className} {...props}>
      {children}
    </Typography>
  );
}

export function Callout({ children, className, ...props }: Omit<TypographyProps, 'variant'>) {
  return (
    <Typography variant="callout" className={className} {...props}>
      {children}
    </Typography>
  );
}

export function Subhead({ children, className, ...props }: Omit<TypographyProps, 'variant'>) {
  return (
    <Typography variant="subhead" className={className} {...props}>
      {children}
    </Typography>
  );
}

export function Footnote({ children, className, ...props }: Omit<TypographyProps, 'variant'>) {
  return (
    <Typography variant="footnote" className={className} {...props}>
      {children}
    </Typography>
  );
}

export function Caption1({ children, className, ...props }: Omit<TypographyProps, 'variant'>) {
  return (
    <Typography variant="caption-1" className={className} {...props}>
      {children}
    </Typography>
  );
}

export function Caption2({ children, className, ...props }: Omit<TypographyProps, 'variant'>) {
  return (
    <Typography variant="caption-2" className={className} {...props}>
      {children}
    </Typography>
  );
}
