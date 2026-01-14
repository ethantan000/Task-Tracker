'use client';

/**
 * Tab Navigation Component with sliding indicator (Apple-style)
 */

import { motion } from 'framer-motion';
import { useState, useRef, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { Typography } from '@/components/atoms/Typography';
import { springs } from '@/lib/animations';

export interface Tab {
  id: string;
  label: string;
  icon?: React.ReactNode;
}

export interface TabNavigationProps {
  tabs: Tab[];
  activeTab: string;
  onChange: (tabId: string) => void;
  className?: string;
}

export function TabNavigation({ tabs, activeTab, onChange, className }: TabNavigationProps) {
  const [indicatorStyle, setIndicatorStyle] = useState({ left: 0, width: 0 });
  const tabRefs = useRef<Map<string, HTMLButtonElement>>(new Map());

  useEffect(() => {
    const activeTabElement = tabRefs.current.get(activeTab);
    if (activeTabElement) {
      setIndicatorStyle({
        left: activeTabElement.offsetLeft,
        width: activeTabElement.offsetWidth,
      });
    }
  }, [activeTab]);

  return (
    <div className={cn('relative', className)}>
      {/* Container */}
      <div className="glass-card p-2 inline-flex gap-2 relative">
        {/* Sliding Indicator */}
        <motion.div
          className="absolute top-2 bottom-2 bg-white/60 backdrop-blur-md rounded-apple-lg shadow-glass-sm"
          initial={false}
          animate={{
            left: indicatorStyle.left,
            width: indicatorStyle.width,
          }}
          transition={springs.smooth}
        />

        {/* Tabs */}
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;

          return (
            <motion.button
              key={tab.id}
              ref={(el) => {
                if (el) tabRefs.current.set(tab.id, el);
              }}
              className={cn(
                'relative z-10 px-6 py-3 rounded-apple-lg transition-colors',
                'focus-ring font-semibold',
                isActive ? 'text-text-primary' : 'text-text-secondary hover:text-text-primary'
              )}
              onClick={() => onChange(tab.id)}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              transition={springs.snappy}
            >
              <div className="flex items-center gap-2">
                {tab.icon && <span>{tab.icon}</span>}
                <Typography variant="headline" as="span">
                  {tab.label}
                </Typography>
              </div>
            </motion.button>
          );
        })}
      </div>
    </div>
  );
}

export function TabNavigationMobile({
  tabs,
  activeTab,
  onChange,
  className,
}: TabNavigationProps) {
  return (
    <div className={cn('overflow-x-auto scrollbar-none', className)}>
      <div className="glass-card p-2 inline-flex gap-2 min-w-full">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;

          return (
            <motion.button
              key={tab.id}
              className={cn(
                'px-4 py-2 rounded-apple font-medium text-subhead whitespace-nowrap',
                'transition-colors focus-ring',
                isActive
                  ? 'bg-white/60 text-text-primary shadow-glass-sm'
                  : 'text-text-secondary hover:text-text-primary hover:bg-white/30'
              )}
              onClick={() => onChange(tab.id)}
              whileTap={{ scale: 0.95 }}
              transition={springs.snappy}
            >
              <div className="flex items-center gap-2">
                {tab.icon && <span className="text-sm">{tab.icon}</span>}
                {tab.label}
              </div>
            </motion.button>
          );
        })}
      </div>
    </div>
  );
}
