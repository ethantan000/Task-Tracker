'use client';

/**
 * Screenshot Thumbnail Component
 * Displays a single screenshot with glassmorphic styling
 */

import { motion } from 'framer-motion';
import Image from 'next/image';
import { Typography } from '@/components/atoms/Typography';
import { Badge } from '@/components/atoms/Badge';
import { formatTimeOnly } from '@/lib/utils';
import { cn } from '@/lib/utils';
import type { Screenshot as ScreenshotType } from '@/types/activity';

export interface ScreenshotProps {
  screenshot: ScreenshotType;
  onClick: () => void;
  index: number;
}

export function Screenshot({ screenshot, onClick, index }: ScreenshotProps) {
  const isLoading = false; // Can add loading state if needed

  return (
    <motion.div
      className="glass-card p-3 cursor-pointer group"
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: index * 0.03, type: 'spring', stiffness: 300, damping: 30 }}
      whileHover={{ y: -4, scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
    >
      {/* Image Container */}
      <div className="relative aspect-video w-full mb-3 rounded-apple-lg overflow-hidden bg-background-tertiary">
        {screenshot.url ? (
          <img
            src={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}${screenshot.url}`}
            alt={`Screenshot from ${formatTimeOnly(screenshot.time)}`}
            className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-text-tertiary">
            <svg
              className="w-12 h-12"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
          </div>
        )}

        {/* Suspicious Badge Overlay */}
        {screenshot.suspicious && (
          <div className="absolute top-2 right-2">
            <Badge variant="warning" size="sm" icon="⚠️">
              Suspicious
            </Badge>
          </div>
        )}

        {/* Hover Overlay */}
        <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors duration-300 flex items-center justify-center">
          <motion.div
            initial={{ scale: 0 }}
            whileHover={{ scale: 1 }}
            className="w-12 h-12 rounded-full bg-white/90 backdrop-blur-sm flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
          >
            <svg
              className="w-6 h-6 text-text-primary"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7"
              />
            </svg>
          </motion.div>
        </div>
      </div>

      {/* Screenshot Info */}
      <div className="space-y-1">
        <Typography variant="callout" weight="semibold" className="truncate">
          {formatTimeOnly(screenshot.time)}
        </Typography>
        <Typography variant="caption-1" color="secondary" className="truncate">
          Click to view full size
        </Typography>
      </div>
    </motion.div>
  );
}
