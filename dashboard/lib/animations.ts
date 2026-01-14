/**
 * Framer Motion animation presets (Apple-style spring physics)
 */

import { Variants, Transition } from 'framer-motion';

// Spring transition presets
export const springs = {
  // Snappy (buttons, toggles)
  snappy: {
    type: 'spring',
    stiffness: 400,
    damping: 30,
  } as Transition,

  // Smooth (cards, modals)
  smooth: {
    type: 'spring',
    stiffness: 300,
    damping: 35,
  } as Transition,

  // Gentle (page transitions)
  gentle: {
    type: 'spring',
    stiffness: 200,
    damping: 40,
  } as Transition,

  // Bouncy (success states)
  bouncy: {
    type: 'spring',
    stiffness: 500,
    damping: 25,
  } as Transition,
};

// Common animation variants
export const fadeIn: Variants = {
  hidden: {
    opacity: 0,
    y: 10,
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: springs.smooth,
  },
};

export const fadeInUp: Variants = {
  hidden: {
    opacity: 0,
    y: 20,
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: springs.smooth,
  },
};

export const fadeInDown: Variants = {
  hidden: {
    opacity: 0,
    y: -20,
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: springs.smooth,
  },
};

export const slideInLeft: Variants = {
  hidden: {
    opacity: 0,
    x: -30,
  },
  visible: {
    opacity: 1,
    x: 0,
    transition: springs.smooth,
  },
};

export const slideInRight: Variants = {
  hidden: {
    opacity: 0,
    x: 30,
  },
  visible: {
    opacity: 1,
    x: 0,
    transition: springs.smooth,
  },
};

export const scaleIn: Variants = {
  hidden: {
    opacity: 0,
    scale: 0.9,
  },
  visible: {
    opacity: 1,
    scale: 1,
    transition: springs.bouncy,
  },
};

export const scaleInLarge: Variants = {
  hidden: {
    opacity: 0,
    scale: 0.8,
  },
  visible: {
    opacity: 1,
    scale: 1,
    transition: springs.smooth,
  },
};

// Staggered children animations
export const staggerContainer: Variants = {
  hidden: {
    opacity: 0,
  },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
      delayChildren: 0.1,
    },
  },
};

export const staggerItem: Variants = {
  hidden: {
    opacity: 0,
    y: 20,
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: springs.smooth,
  },
};

// Hover animations
export const hoverLift = {
  rest: {
    y: 0,
    scale: 1,
  },
  hover: {
    y: -4,
    scale: 1.02,
    transition: springs.snappy,
  },
  tap: {
    scale: 0.98,
    transition: springs.snappy,
  },
};

export const hoverScale = {
  rest: {
    scale: 1,
  },
  hover: {
    scale: 1.05,
    transition: springs.snappy,
  },
  tap: {
    scale: 0.95,
    transition: springs.snappy,
  },
};

// Modal/Dialog animations
export const modalBackdrop: Variants = {
  hidden: {
    opacity: 0,
  },
  visible: {
    opacity: 1,
    transition: {
      duration: 0.2,
    },
  },
  exit: {
    opacity: 0,
    transition: {
      duration: 0.2,
    },
  },
};

export const modalContent: Variants = {
  hidden: {
    opacity: 0,
    scale: 0.95,
    y: 20,
  },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: springs.smooth,
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    y: 20,
    transition: springs.snappy,
  },
};

// Tab switching animation
export const tabContent: Variants = {
  hidden: {
    opacity: 0,
    x: -20,
  },
  visible: {
    opacity: 1,
    x: 0,
    transition: springs.gentle,
  },
  exit: {
    opacity: 0,
    x: 20,
    transition: springs.gentle,
  },
};

// Number counter animation
export const numberCounter: Variants = {
  hidden: {
    opacity: 0,
    scale: 0.8,
  },
  visible: {
    opacity: 1,
    scale: 1,
    transition: springs.bouncy,
  },
};

// Progress ring animation
export const progressRing: Variants = {
  hidden: {
    pathLength: 0,
    opacity: 0,
  },
  visible: (custom: number) => ({
    pathLength: custom,
    opacity: 1,
    transition: {
      pathLength: {
        type: 'spring',
        stiffness: 100,
        damping: 20,
        duration: 1,
      },
      opacity: {
        duration: 0.2,
      },
    },
  }),
};

// Skeleton loading animation
export const skeletonPulse: Variants = {
  initial: {
    opacity: 0.6,
  },
  animate: {
    opacity: 1,
    transition: {
      duration: 0.8,
      repeat: Infinity,
      repeatType: 'reverse',
      ease: 'easeInOut',
    },
  },
};

// Page transition
export const pageTransition: Variants = {
  initial: {
    opacity: 0,
    y: 20,
  },
  animate: {
    opacity: 1,
    y: 0,
    transition: springs.gentle,
  },
  exit: {
    opacity: 0,
    y: -20,
    transition: springs.gentle,
  },
};

// List item with drag indicator
export const listItem: Variants = {
  hidden: {
    opacity: 0,
    x: -20,
  },
  visible: (custom: number) => ({
    opacity: 1,
    x: 0,
    transition: {
      ...springs.smooth,
      delay: custom * 0.05,
    },
  }),
};

// Notification toast
export const toast: Variants = {
  hidden: {
    opacity: 0,
    y: -50,
    scale: 0.9,
  },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: springs.bouncy,
  },
  exit: {
    opacity: 0,
    scale: 0.9,
    transition: springs.snappy,
  },
};

// Expandable section
export const expandableSection: Variants = {
  collapsed: {
    height: 0,
    opacity: 0,
  },
  expanded: {
    height: 'auto',
    opacity: 1,
    transition: springs.smooth,
  },
};
