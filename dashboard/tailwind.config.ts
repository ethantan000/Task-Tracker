import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      // Apple 2025 Color Palette
      colors: {
        background: {
          primary: '#f5f5f7',
          secondary: '#ffffff',
          tertiary: '#fafafa',
        },
        glass: {
          light: 'rgba(255, 255, 255, 0.7)',
          medium: 'rgba(255, 255, 255, 0.5)',
          dark: 'rgba(255, 255, 255, 0.3)',
        },
        text: {
          primary: '#1d1d1f',
          secondary: '#86868b',
          tertiary: '#c7c7cc',
        },
        accent: '#0a84ff',
        success: '#34c759',
        warning: '#ff9f0a',
        error: '#ff3b30',
        border: {
          light: 'rgba(0, 0, 0, 0.04)',
          medium: 'rgba(0, 0, 0, 0.08)',
          strong: 'rgba(0, 0, 0, 0.12)',
        },
      },

      // SF Pro Typography
      fontFamily: {
        display: ['-apple-system', 'BlinkMacSystemFont', 'SF Pro Display', 'Helvetica Neue', 'sans-serif'],
        text: ['-apple-system', 'BlinkMacSystemFont', 'SF Pro Text', 'Helvetica Neue', 'sans-serif'],
        mono: ['ui-monospace', 'SF Mono', 'Menlo', 'Monaco', 'monospace'],
      },

      // Apple Typography Scale
      fontSize: {
        'display-large': ['72px', { lineHeight: '1.05', fontWeight: '700' }],
        'display': ['48px', { lineHeight: '1.1', fontWeight: '700' }],
        'title-1': ['34px', { lineHeight: '1.2', fontWeight: '600' }],
        'title-2': ['28px', { lineHeight: '1.25', fontWeight: '600' }],
        'title-3': ['22px', { lineHeight: '1.3', fontWeight: '600' }],
        'headline': ['17px', { lineHeight: '1.35', fontWeight: '600' }],
        'body': ['17px', { lineHeight: '1.5', fontWeight: '400' }],
        'callout': ['16px', { lineHeight: '1.4', fontWeight: '400' }],
        'subhead': ['15px', { lineHeight: '1.4', fontWeight: '400' }],
        'footnote': ['13px', { lineHeight: '1.4', fontWeight: '400' }],
        'caption-1': ['12px', { lineHeight: '1.35', fontWeight: '400' }],
        'caption-2': ['11px', { lineHeight: '1.3', fontWeight: '400' }],
      },

      // Glassmorphic Shadows
      boxShadow: {
        'glass': '0 0 0 0.5px rgba(0, 0, 0, 0.04), 0 2px 4px rgba(0, 0, 0, 0.02), 0 8px 16px rgba(0, 0, 0, 0.04), 0 16px 32px rgba(0, 0, 0, 0.04)',
        'glass-hover': '0 0 0 0.5px rgba(0, 0, 0, 0.06), 0 4px 8px rgba(0, 0, 0, 0.04), 0 12px 24px rgba(0, 0, 0, 0.06), 0 24px 48px rgba(0, 0, 0, 0.08)',
        'glass-sm': '0 0 0 0.5px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.02), 0 4px 8px rgba(0, 0, 0, 0.03)',
        'glass-lg': '0 0 0 0.5px rgba(0, 0, 0, 0.06), 0 8px 16px rgba(0, 0, 0, 0.06), 0 20px 40px rgba(0, 0, 0, 0.08), 0 32px 64px rgba(0, 0, 0, 0.1)',
      },

      // Border Radius (Apple style)
      borderRadius: {
        'apple-sm': '8px',
        'apple': '12px',
        'apple-lg': '16px',
        'apple-xl': '20px',
        'apple-2xl': '24px',
      },

      // Z-Index Layers
      zIndex: {
        'base': '0',
        'dropdown': '1000',
        'sticky': '1020',
        'fixed': '1030',
        'modal-backdrop': '1040',
        'modal': '1050',
        'popover': '1060',
        'tooltip': '1070',
      },

      // Backdrop Blur
      backdropBlur: {
        'glass': '20px',
        'glass-lg': '40px',
      },

      // Backdrop Saturate
      backdropSaturate: {
        'glass': '180%',
      },

      // Spring Animation Curves
      transitionTimingFunction: {
        'spring-snappy': 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
        'spring-smooth': 'cubic-bezier(0.23, 1, 0.32, 1)',
        'spring-gentle': 'cubic-bezier(0.34, 1.56, 0.64, 1)',
        'spring-bouncy': 'cubic-bezier(0.175, 0.885, 0.32, 1.275)',
      },

      // Responsive Breakpoints
      screens: {
        'mobile': '320px',
        'sm': '640px',
        'md': '768px',
        'lg': '1024px',
        'xl': '1280px',
        '2xl': '1536px',
        '4k': '2560px',
      },
    },
  },
  plugins: [],
}

export default config
