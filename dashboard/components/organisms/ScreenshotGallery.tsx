'use client';

/**
 * Screenshot Gallery Component
 * Responsive grid with masonry-like layout
 */

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Typography } from '@/components/atoms/Typography';
import { Screenshot } from '@/components/molecules/Screenshot';
import { ScreenshotLightbox } from '@/components/organisms/ScreenshotLightbox';
import { staggerContainer } from '@/lib/animations';
import type { Screenshot as ScreenshotType } from '@/types/activity';

export interface ScreenshotGalleryProps {
  screenshots: ScreenshotType[];
  title?: string;
  emptyMessage?: string;
  maxDisplay?: number;
}

export function ScreenshotGallery({
  screenshots,
  title = 'Screenshots',
  emptyMessage = 'No screenshots captured yet',
  maxDisplay,
}: ScreenshotGalleryProps) {
  const [lightboxOpen, setLightboxOpen] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);

  const displayScreenshots = maxDisplay ? screenshots.slice(0, maxDisplay) : screenshots;

  const openLightbox = (index: number) => {
    setCurrentIndex(index);
    setLightboxOpen(true);
  };

  const handleNext = () => {
    if (currentIndex < screenshots.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  if (screenshots.length === 0) {
    return (
      <div className="glass-card p-12 text-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
        >
          <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-background-tertiary flex items-center justify-center">
            <svg
              className="w-10 h-10 text-text-tertiary"
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
          <Typography variant="headline" weight="semibold" className="mb-2">
            {emptyMessage}
          </Typography>
          <Typography variant="body" color="secondary">
            Screenshots will appear here as activity is tracked
          </Typography>
        </motion.div>
      </div>
    );
  }

  return (
    <>
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <Typography variant="title-3" weight="semibold">
            {title}
          </Typography>
          <Typography variant="subhead" color="secondary">
            {screenshots.length} {screenshots.length === 1 ? 'screenshot' : 'screenshots'}
          </Typography>
        </div>

        {/* Grid */}
        <motion.div
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4"
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
        >
          {displayScreenshots.map((screenshot, index) => (
            <Screenshot
              key={`${screenshot.time}-${index}`}
              screenshot={screenshot}
              onClick={() => openLightbox(index)}
              index={index}
            />
          ))}
        </motion.div>

        {/* Show More Message */}
        {maxDisplay && screenshots.length > maxDisplay && (
          <div className="text-center py-4">
            <Typography variant="callout" color="secondary">
              +{screenshots.length - maxDisplay} more screenshots available
            </Typography>
          </div>
        )}
      </div>

      {/* Lightbox Modal */}
      <ScreenshotLightbox
        screenshots={screenshots}
        currentIndex={currentIndex}
        isOpen={lightboxOpen}
        onClose={() => setLightboxOpen(false)}
        onNext={handleNext}
        onPrevious={handlePrevious}
      />
    </>
  );
}
