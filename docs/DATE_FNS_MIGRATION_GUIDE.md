# date-fns Migration Guide

## Overview

This guide helps you replace the heavy `date-fns` library (24MB) with lighter alternatives, reducing your `node_modules` size by ~90% for date operations.

---

## Current Usage Analysis

**Files using date-fns:**
- `dashboard/lib/utils.ts` - 3 functions use date-fns
- `dashboard/package.json` - Listed as dependency

**Functions affected:**
1. `formatDate()` - Uses `format()` and `parseISO()`
2. `formatTimeOnly()` - Uses `format()` and `parseISO()`
3. `formatRelativeTime()` - Uses `formatDistanceToNow()` and `parseISO()`

---

## Migration Options

### **Option 1: Native JavaScript Intl API (Recommended)**

**Pros:**
- ✅ Zero bytes (built into browser/Node.js)
- ✅ No dependencies
- ✅ Well-supported (IE11+, all modern browsers)
- ✅ Handles timezones properly

**Cons:**
- ❌ More verbose API
- ❌ Limited formatting options compared to date-fns

**Size savings:** 24MB → 0MB (100% reduction)

---

### **Option 2: day.js (Alternative lightweight library)**

**Pros:**
- ✅ Only 2KB gzipped (vs 24MB for date-fns)
- ✅ Similar API to date-fns/moment.js
- ✅ Plugin system for advanced features
- ✅ Immutable & chainable

**Cons:**
- ❌ Still a dependency to manage
- ❌ Requires plugins for some features

**Size savings:** 24MB → 2KB (99.99% reduction)

---

## Implementation: Option 1 (Native Intl)

### Step 1: Install no dependencies
```bash
# No installation needed! 🎉
```

### Step 2: Update `dashboard/lib/utils.ts`

**Replace the imports:**
```typescript
// REMOVE:
import { format, parseISO, formatDistanceToNow } from 'date-fns';

// NO IMPORT NEEDED - using native Intl API
```

**Replace formatDate():**
```typescript
/**
 * Format ISO timestamp to readable date
 */
export function formatDate(isoString: string, formatStr: string = 'MMM d, yyyy'): string {
  try {
    const date = new Date(isoString);

    // Map formatStr to Intl options
    if (formatStr === 'MMM d, yyyy') {
      return new Intl.DateTimeFormat('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      }).format(date);
    }

    if (formatStr === 'EEEE, MMMM d, yyyy') {
      return new Intl.DateTimeFormat('en-US', {
        weekday: 'long',
        month: 'long',
        day: 'numeric',
        year: 'numeric'
      }).format(date);
    }

    if (formatStr === 'EEE, MMM d') {
      return new Intl.DateTimeFormat('en-US', {
        weekday: 'short',
        month: 'short',
        day: 'numeric'
      }).format(date);
    }

    if (formatStr === 'EEEE') {
      return new Intl.DateTimeFormat('en-US', { weekday: 'long' }).format(date);
    }

    if (formatStr === 'MMMM') {
      return new Intl.DateTimeFormat('en-US', { month: 'long' }).format(date);
    }

    // Default fallback
    return new Intl.DateTimeFormat('en-US').format(date);
  } catch {
    return isoString;
  }
}
```

**Replace formatTimeOnly():**
```typescript
/**
 * Format ISO timestamp to time only
 */
export function formatTimeOnly(isoString: string): string {
  try {
    const date = new Date(isoString);
    return new Intl.DateTimeFormat('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    }).format(date);
  } catch {
    return isoString;
  }
}
```

**Replace formatRelativeTime():**
```typescript
/**
 * Get relative time (e.g., "2 hours ago")
 */
export function formatRelativeTime(isoString: string): string {
  try {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffSecs = Math.floor(diffMs / 1000);
    const diffMins = Math.floor(diffSecs / 60);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffSecs < 60) {
      return 'just now';
    } else if (diffMins < 60) {
      return `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`;
    } else if (diffHours < 24) {
      return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
    } else if (diffDays < 30) {
      return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
    } else {
      const diffMonths = Math.floor(diffDays / 30);
      return `${diffMonths} month${diffMonths !== 1 ? 's' : ''} ago`;
    }
  } catch {
    return isoString;
  }
}
```

**Also update these helper functions:**
```typescript
/**
 * Get day of week name
 */
export function getDayName(dateString: string): string {
  try {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', { weekday: 'long' }).format(date);
  } catch {
    return '';
  }
}

/**
 * Get month name
 */
export function getMonthName(dateString: string): string {
  try {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', { month: 'long' }).format(date);
  } catch {
    return '';
  }
}
```

### Step 3: Remove date-fns from package.json

```bash
cd dashboard
npm uninstall date-fns
```

### Step 4: Test the changes

```bash
cd dashboard
npm run build
npm run dev
```

**Manual testing checklist:**
- [ ] Dashboard header shows correct date format (e.g., "Monday, January 14, 2026")
- [ ] Daily breakdown shows dates correctly (e.g., "Mon, Jan 14")
- [ ] Activity stats display properly
- [ ] No console errors related to date formatting

---

## Implementation: Option 2 (day.js)

### Step 1: Install day.js

```bash
cd dashboard
npm uninstall date-fns
npm install dayjs
```

**Size comparison:**
- Before: 24MB (date-fns)
- After: 2KB (day.js)
- Savings: 23.998MB

### Step 2: Update `dashboard/lib/utils.ts`

**Replace the imports:**
```typescript
// REMOVE:
import { format, parseISO, formatDistanceToNow } from 'date-fns';

// ADD:
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';

dayjs.extend(relativeTime);
```

**Replace formatDate():**
```typescript
/**
 * Format ISO timestamp to readable date
 */
export function formatDate(isoString: string, formatStr: string = 'MMM D, YYYY'): string {
  try {
    return dayjs(isoString).format(formatStr);
  } catch {
    return isoString;
  }
}
```

**Replace formatTimeOnly():**
```typescript
/**
 * Format ISO timestamp to time only
 */
export function formatTimeOnly(isoString: string): string {
  try {
    return dayjs(isoString).format('h:mm A');
  } catch {
    return isoString;
  }
}
```

**Replace formatRelativeTime():**
```typescript
/**
 * Get relative time (e.g., "2 hours ago")
 */
export function formatRelativeTime(isoString: string): string {
  try {
    return dayjs(isoString).fromNow();
  } catch {
    return isoString;
  }
}
```

**Update helper functions:**
```typescript
/**
 * Get day of week name
 */
export function getDayName(dateString: string): string {
  try {
    return dayjs(dateString).format('dddd');
  } catch {
    return '';
  }
}

/**
 * Get month name
 */
export function getMonthName(dateString: string): string {
  try {
    return dayjs(dateString).format('MMMM');
  } catch {
    return '';
  }
}
```

**Note on format tokens:**
- date-fns: `yyyy-MM-dd` → day.js: `YYYY-MM-DD`
- date-fns: `EEEE` (weekday) → day.js: `dddd`
- date-fns: `MMMM` (month) → day.js: `MMMM` (same)

### Step 3: Test the changes

```bash
cd dashboard
npm run build
npm run dev
```

---

## Format String Mapping

If you use custom format strings, here's a conversion chart:

| date-fns Token | day.js Token | Intl API Option | Output Example |
|----------------|--------------|-----------------|----------------|
| `yyyy` | `YYYY` | `year: 'numeric'` | 2026 |
| `yy` | `YY` | `year: '2-digit'` | 26 |
| `MMMM` | `MMMM` | `month: 'long'` | January |
| `MMM` | `MMM` | `month: 'short'` | Jan |
| `MM` | `MM` | `month: '2-digit'` | 01 |
| `dd` | `DD` | `day: '2-digit'` | 14 |
| `d` | `D` | `day: 'numeric'` | 14 |
| `EEEE` | `dddd` | `weekday: 'long'` | Monday |
| `EEE` | `ddd` | `weekday: 'short'` | Mon |
| `HH` | `HH` | `hour: '2-digit'` | 14 |
| `h` | `h` | `hour: 'numeric'` | 2 |
| `mm` | `mm` | `minute: '2-digit'` | 05 |
| `ss` | `ss` | `second: '2-digit'` | 30 |
| `a` | `A` | `hour12: true` | PM |

---

## Rollback Plan

If you encounter issues:

```bash
# Restore date-fns
cd dashboard
npm install date-fns@^4.1.0

# Restore original utils.ts from git
git checkout dashboard/lib/utils.ts
```

---

## Expected Results

### Bundle Size Reduction:
- **Before:** 569MB total, 24MB from date-fns
- **After (Native Intl):** 545MB total, 0MB from date-fns
- **After (day.js):** 545MB total, 2KB from day.js

### Build Performance:
- Faster `npm install` (fewer packages to download)
- Faster production builds (less code to minify)
- Smaller runtime bundle size

### Runtime Performance:
- Native Intl: Slightly faster (no library overhead)
- day.js: Similar performance to date-fns

---

## Troubleshooting

### Issue: "Intl is not defined"
**Solution:** Your Node.js version is too old (pre-v13). Upgrade Node.js or use day.js instead.

### Issue: Date formats look different
**Solution:** Intl API uses locale-specific formatting. Pin the locale:
```typescript
new Intl.DateTimeFormat('en-US', options).format(date)
```

### Issue: "Cannot read property 'format' of undefined"
**Solution:** Ensure date strings are valid ISO 8601 format. Add validation:
```typescript
const date = new Date(isoString);
if (isNaN(date.getTime())) {
  return isoString; // Invalid date
}
```

---

## Additional Optimization

After migrating, consider removing other unused date utilities from `utils.ts`:
- `formatTimeDetailed()` - Not used in codebase
- `getDayName()` - Only used in one place (inline it?)
- `getMonthName()` - Only used in one place (inline it?)

---

## Questions?

See the main optimization guide or check:
- [MDN: Intl.DateTimeFormat](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/DateTimeFormat)
- [day.js Documentation](https://day.js.org/)
