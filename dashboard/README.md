# Task-Tracker Dashboard v2.0

**A Vision Pro-level, Apple-inspired activity monitoring dashboard with production-grade reliability.**

## 🎨 Design Philosophy

- **Materials**: Heavy glassmorphism with ultra-fine 0.5px borders and dynamic blurring
- **Typography**: Apple SF Pro Display/Text hierarchy with aggressive weight contrast
- **Depth**: Layered z-axis stacking with expansive box shadows
- **Interaction**: Fluid, spring-based transitions (Apple-style physics)
- **Responsive**: Flawless from 4K displays down to mobile devices

## ✨ Features

### Real-time Monitoring
- Live WebSocket updates every 5 seconds
- Auto-refresh data every 30 seconds
- Real-time status indicators with pulse animations

### Multi-Period Views
- **Daily**: Today's activity with detailed breakdown
- **Weekly**: 7-day summary with daily comparisons
- **Monthly**: Month-at-a-glance analytics
- **Yearly**: Annual totals and productivity trends

### Comprehensive Metrics
- Work time tracking
- Idle time detection
- Anti-cheat suspicious activity flagging
- Real work calculation (verified activity)
- Screenshot count and management
- Keyboard activity tracking
- Window switch monitoring

### Apple-Grade UX
- Glassmorphic UI components
- Spring physics animations (Framer Motion)
- Smooth tab transitions
- Loading skeletons
- Error boundaries
- Empty states
- Responsive grid layouts
- Optimized for 4K displays

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.10+ (for API backend)
- Running Task-Tracker monitoring app

### Installation

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Configure environment**
   ```bash
   cp .env.local.example .env.local
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```

4. **Open dashboard**
   Navigate to [http://localhost:3000](http://localhost:3000)

### Running with API Backend

The dashboard requires the FastAPI backend to be running:

```bash
# In a separate terminal, start the API server
cd ../api
pip install -r requirements.txt
python main.py

# Or use the start script
./start.sh
```

The API will be available at `http://localhost:8000` with:
- REST API endpoints: `/api/*`
- WebSocket: `ws://localhost:8000/ws/activity`
- API docs: `http://localhost:8000/docs`

## 📁 Project Structure

```
dashboard/
├── app/                          # Next.js App Router
│   ├── layout.tsx               # Root layout
│   ├── page.tsx                 # Main dashboard
│   └── globals.css              # Global styles + glassmorphism
│
├── components/
│   ├── atoms/                   # Base components
│   │   ├── Button.tsx          # Glassmorphic buttons
│   │   ├── Badge.tsx           # Status badges
│   │   ├── Skeleton.tsx        # Loading states
│   │   └── Typography.tsx      # SF Pro typography
│   │
│   ├── molecules/               # Composite components
│   │   ├── StatCard.tsx        # Metric cards
│   │   └── TabNavigation.tsx   # Tab switcher
│   │
│   └── providers/
│       └── QueryProvider.tsx   # React Query setup
│
├── hooks/
│   └── useActivityData.ts      # Data fetching hooks
│
├── lib/
│   ├── api.ts                  # API client
│   ├── utils.ts                # Utility functions
│   └── animations.ts           # Framer Motion presets
│
├── types/
│   └── activity.ts             # TypeScript definitions
│
├── tailwind.config.ts          # Apple design tokens
└── next.config.js              # Next.js configuration
```

## 🎨 Design Tokens

### Colors
```typescript
background: {
  primary: '#f5f5f7',    // Main background
  secondary: '#ffffff',  // Cards
  tertiary: '#fafafa',   // Elevated surfaces
}

glass: {
  light: 'rgba(255, 255, 255, 0.7)',
  medium: 'rgba(255, 255, 255, 0.5)',
  dark: 'rgba(255, 255, 255, 0.3)',
}

semantic: {
  success: '#34c759',    // Green (work)
  warning: '#ff9f0a',    // Orange (suspicious)
  error: '#ff3b30',      // Red (idle)
  accent: '#0a84ff',     // Blue (accent)
}
```

### Typography Scale
- **display-large**: 72px / 700 weight
- **display**: 48px / 700 weight
- **title-1**: 34px / 600 weight
- **title-2**: 28px / 600 weight
- **title-3**: 22px / 600 weight
- **headline**: 17px / 600 weight
- **body**: 17px / 400 weight
- **footnote**: 13px / 400 weight
- **caption**: 12px / 400 weight

### Animations
```typescript
springs: {
  snappy: { stiffness: 400, damping: 30 },  // Buttons
  smooth: { stiffness: 300, damping: 35 },  // Cards
  gentle: { stiffness: 200, damping: 40 },  // Pages
  bouncy: { stiffness: 500, damping: 25 },  // Success
}
```

## 🔌 API Integration

### REST Endpoints
```typescript
GET  /api/activity/today          # Today's data
GET  /api/activity/week           # Week summary
GET  /api/activity/month          # Month summary
GET  /api/activity/year           # Year summary
GET  /api/stats/{period}          # Formatted stats
GET  /api/screenshots/today       # Screenshots
GET  /api/config                  # Configuration
```

### WebSocket
```typescript
WS   /ws/activity                 # Real-time updates

// Message format:
{
  type: 'activity_update' | 'pong',
  timestamp: string
}
```

### React Query Caching
- **Stale Time**: 25 seconds
- **Refetch Interval**: 30 seconds
- **Retries**: 3 attempts with exponential backoff
- **Window Focus**: Auto-refetch on tab focus

## 📱 Responsive Breakpoints

```typescript
mobile: '320px'   // iPhone SE
sm: '640px'       // Small tablets
md: '768px'       // iPad portrait
lg: '1024px'      // iPad landscape
xl: '1280px'      // Desktop
2xl: '1536px'     // Large desktop
4k: '2560px'      // 4K displays
```

### Layout Behavior
- **4K/2XL**: 4-column grid, max-width 2000px
- **Desktop/XL**: 4-column grid
- **Tablet/MD**: 2-column grid
- **Mobile/SM**: 1-column stacked

## 🧪 Development

### Available Scripts
```bash
npm run dev      # Start development server (localhost:3000)
npm run build    # Build for production
npm run start    # Start production server
npm run lint     # Run ESLint
```

### Environment Variables
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws/activity
```

## 🚢 Production Build

### Build Optimization
```bash
npm run build
```

Features:
- Server-side rendering (SSR)
- Static generation where possible
- Automatic code splitting
- Image optimization
- CSS minimization
- Tree shaking

### Performance Targets
- First Contentful Paint: < 1s
- Time to Interactive: < 2s
- Lighthouse Score: 90+

## 🔧 Customization

### Changing Colors
Edit `tailwind.config.ts`:
```typescript
colors: {
  accent: '#0a84ff',  // Change primary accent
  success: '#34c759', // Change success color
  // etc.
}
```

### Adjusting Animations
Edit `lib/animations.ts`:
```typescript
springs: {
  snappy: { stiffness: 400, damping: 30 }, // Modify physics
}
```

### Modifying Refetch Interval
Edit `components/providers/QueryProvider.tsx`:
```typescript
refetchInterval: 30000, // Change to desired ms
```

## 📊 Browser Support

- Chrome 90+
- Safari 15+
- Firefox 88+
- Edge 90+

### Required Features
- CSS backdrop-filter (glassmorphism)
- WebSocket support
- ES2020+
- CSS Grid & Flexbox

## 🐛 Troubleshooting

### WebSocket Connection Issues
```bash
# Check if API is running
curl http://localhost:8000/api/health

# Test WebSocket (using wscat)
npm install -g wscat
wscat -c ws://localhost:8000/ws/activity
```

### Build Errors
```bash
# Clear Next.js cache
rm -rf .next

# Clear node_modules
rm -rf node_modules
npm install
```

### Type Errors
```bash
# Regenerate TypeScript types
npx tsc --noEmit
```

## 📝 License

Copyright © 2026 - Task-Tracker Dashboard

## 🎯 Vision Pro Polish Checklist

- ✅ Glassmorphism with 0.5px borders
- ✅ Spring-based physics animations
- ✅ Apple SF Pro typography hierarchy
- ✅ Real-time WebSocket updates
- ✅ Responsive 4K to mobile
- ✅ Loading skeletons
- ✅ Error boundaries
- ✅ Empty states
- ✅ Accessible (ARIA labels)
- ✅ Smooth tab transitions
- ✅ Hover micro-interactions
- ✅ Production-ready build

---

**Built with Next.js 14, React 18, Tailwind CSS, and Framer Motion**
