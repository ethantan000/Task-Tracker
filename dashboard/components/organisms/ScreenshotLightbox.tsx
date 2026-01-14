'use client';

/**
 * Screenshot Lightbox Modal (Apple-style)
 * Full-screen viewer with keyboard navigation and gestures
 */

import { motion, AnimatePresence } from 'framer-motion';
import { useEffect, useCallback } from 'react';
import { Typography } from '@/components/atoms/Typography';
import { Badge } from '@/components/atoms/Badge';
import { Button } from '@/components/atoms/Button';
import { formatTimeOnly, formatDate } from '@/lib/utils';
import { modalBackdrop, modalContent } from '@/lib/animations';
import type { Screenshot } from '@/types/activity';

export interface ScreenshotLightboxProps {
  screenshots: Screenshot[];
  currentIndex: number;
  isOpen: boolean;
  onClose: () => void;
  onNext: () => void;
  onPrevious: () => void;
}

export function ScreenshotLightbox({
  screenshots,
  currentIndex,
  isOpen,
  onClose,
  onNext,
  onPrevious,
}: ScreenshotLightboxProps) {
  const currentScreenshot = screenshots[currentIndex];
  const hasPrevious = currentIndex > 0;
  const hasNext = currentIndex < screenshots.length - 1;

  // Keyboard navigation
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      switch (e.key) {
        case 'Escape':
          onClose();
          break;
        case 'ArrowLeft':
          if (hasPrevious) onPrevious();
          break;
        case 'ArrowRight':
          if (hasNext) onNext();
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, hasPrevious, hasNext, onClose, onNext, onPrevious]);

  // Prevent body scroll when open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  if (!currentScreenshot) return null;

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            className="fixed inset-0 bg-black/80 backdrop-blur-xl z-modal-backdrop"
            variants={modalBackdrop}
            initial="hidden"
            animate="visible"
            exit="exit"
            onClick={onClose}
          />

          {/* Modal Container */}
          <div className="fixed inset-0 z-modal flex items-center justify-center p-4 sm:p-6 lg:p-8">
            <motion.div
              className="relative w-full max-w-7xl"
              variants={modalContent}
              initial="hidden"
              animate="visible"
              exit="exit"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Header */}
              <div className="glass-card p-4 mb-4 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <Typography variant="headline" weight="semibold">
                    Screenshot {currentIndex + 1} of {screenshots.length}
                  </Typography>
                  <div className="flex items-center gap-2">
                    <Typography variant="subhead" color="secondary">
                      {formatDate(currentScreenshot.time, 'MMM d, yyyy')} •{' '}
                      {formatTimeOnly(currentScreenshot.time)}
                    </Typography>
                    {currentScreenshot.suspicious && (
                      <Badge variant="warning" size="sm" icon="⚠️">
                        Suspicious
                      </Badge>
                    )}
                  </div>
                </div>

                {/* Close Button */}
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onClose}
                  aria-label="Close lightbox"
                  icon={
                    <svg
                      className="w-5 h-5"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M6 18L18 6M6 6l12 12"
                      />
                    </svg>
                  }
                />
              </div>

              {/* Image Container */}
              <div className="glass-card p-6 relative">
                <motion.div
                  key={currentIndex}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  transition={{ duration: 0.2 }}
                  className="relative w-full"
                  style={{ maxHeight: 'calc(100vh - 250px)' }}
                >
                  {currentScreenshot.url ? (
                    <img
                      src={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}${currentScreenshot.url}`}
                      alt={`Screenshot from ${formatTimeOnly(currentScreenshot.time)}`}
                      className="w-full h-full object-contain rounded-apple-lg"
                      style={{ maxHeight: 'calc(100vh - 250px)' }}
                    />
                  ) : (
                    <div className="w-full h-96 flex items-center justify-center bg-background-tertiary rounded-apple-lg">
                      <div className="text-center">
                        <svg
                          className="w-16 h-16 mx-auto mb-4 text-text-tertiary"
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
                        <Typography variant="body" color="secondary">
                          Image not available
                        </Typography>
                      </div>
                    </div>
                  )}
                </motion.div>

                {/* Navigation Buttons */}
                {hasPrevious && (
                  <button
                    onClick={onPrevious}
                    className="absolute left-4 top-1/2 -translate-y-1/2 w-12 h-12 rounded-full glass-card flex items-center justify-center hover:scale-110 active:scale-95 transition-transform"
                    aria-label="Previous screenshot"
                  >
                    <svg
                      className="w-6 h-6"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M15 19l-7-7 7-7"
                      />
                    </svg>
                  </button>
                )}

                {hasNext && (
                  <button
                    onClick={onNext}
                    className="absolute right-4 top-1/2 -translate-y-1/2 w-12 h-12 rounded-full glass-card flex items-center justify-center hover:scale-110 active:scale-95 transition-transform"
                    aria-label="Next screenshot"
                  >
                    <svg
                      className="w-6 h-6"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 5l7 7-7 7"
                      />
                    </svg>
                  </button>
                )}
              </div>

              {/* Footer Info */}
              <div className="glass-card p-4 mt-4 flex items-center justify-between">
                <Typography variant="caption-1" color="secondary">
                  Use ← → arrow keys to navigate, ESC to close
                </Typography>
                <Typography variant="caption-1" color="secondary" mono>
                  {currentScreenshot.path.split('/').pop() || 'Unknown'}
                </Typography>
              </div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
}
