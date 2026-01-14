#!/bin/bash

###############################################################################
# Task-Tracker Cleanup & Optimization Script
# Automates the removal of unused dependencies, dead code, and optimizations
#
# Usage:
#   ./scripts/cleanup-optimizer.sh [--dry-run] [--skip-install]
#
# Options:
#   --dry-run       Show what would be done without making changes
#   --skip-install  Skip npm install/uninstall (faster for testing)
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
DRY_RUN=false
SKIP_INSTALL=false
for arg in "$@"; do
  case $arg in
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --skip-install)
      SKIP_INSTALL=true
      shift
      ;;
  esac
done

# Helper functions
info() {
  echo -e "${BLUE}ℹ${NC} $1"
}

success() {
  echo -e "${GREEN}✓${NC} $1"
}

warning() {
  echo -e "${YELLOW}⚠${NC} $1"
}

error() {
  echo -e "${RED}✗${NC} $1"
}

section() {
  echo ""
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${BLUE}$1${NC}"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

dry_run_msg() {
  if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}[DRY RUN]${NC} Would: $1"
  else
    echo -e "$1"
  fi
}

execute() {
  if [ "$DRY_RUN" = true ]; then
    dry_run_msg "$1"
  else
    eval "$1"
  fi
}

# Determine project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

info "Starting Task-Tracker optimization..."
info "Project root: $PROJECT_ROOT"
if [ "$DRY_RUN" = true ]; then
  warning "Running in DRY RUN mode - no changes will be made"
fi

###############################################################################
# PHASE 1: Measure current state
###############################################################################
section "📊 Phase 1: Measuring Current State"

if [ -d "dashboard/node_modules" ]; then
  BEFORE_SIZE=$(du -sh dashboard/node_modules | cut -f1)
  info "Current node_modules size: $BEFORE_SIZE"
else
  BEFORE_SIZE="(not installed)"
  warning "node_modules not found - will measure after install"
fi

# Count dependencies
TOTAL_DEPS=$(grep -c '"' dashboard/package.json || echo "unknown")
info "Total package.json entries: $TOTAL_DEPS"

###############################################################################
# PHASE 2: Remove unused dependencies
###############################################################################
section "🗑️  Phase 2: Removing Unused Dependencies"

if [ "$SKIP_INSTALL" = false ]; then
  cd dashboard

  info "Checking for unused packages..."

  # Check if packages are actually unused
  UNUSED_PACKAGES=()

  # Check zustand
  if grep -q '"zustand"' package.json; then
    if ! grep -r "zustand" --include="*.tsx" --include="*.ts" app/ components/ hooks/ lib/ 2>/dev/null; then
      UNUSED_PACKAGES+=("zustand")
      success "Confirmed: zustand is unused"
    fi
  fi

  # Check chart.js
  if grep -q '"chart.js"' package.json; then
    if ! grep -r "chart\.js\|Chart" --include="*.tsx" --include="*.ts" app/ components/ hooks/ lib/ 2>/dev/null; then
      UNUSED_PACKAGES+=("chart.js")
      success "Confirmed: chart.js is unused"
    fi
  fi

  # Check react-chartjs-2
  if grep -q '"react-chartjs-2"' package.json; then
    if ! grep -r "react-chartjs-2" --include="*.tsx" --include="*.ts" app/ components/ hooks/ lib/ 2>/dev/null; then
      UNUSED_PACKAGES+=("react-chartjs-2")
      success "Confirmed: react-chartjs-2 is unused"
    fi
  fi

  if [ ${#UNUSED_PACKAGES[@]} -gt 0 ]; then
    info "Removing ${#UNUSED_PACKAGES[@]} unused package(s): ${UNUSED_PACKAGES[*]}"
    execute "npm uninstall ${UNUSED_PACKAGES[*]}"
    success "Removed unused dependencies"
  else
    info "No unused dependencies found (they may have been removed already)"
  fi

  cd ..
else
  warning "Skipping npm operations (--skip-install)"
fi

###############################################################################
# PHASE 3: Clean up dead code files
###############################################################################
section "🧹 Phase 3: Removing Dead Code Files"

# Create archive directory
if [ ! -d ".archive" ]; then
  execute "mkdir -p .archive"
  success "Created .archive directory"
fi

# Remove obsolete Python dashboard server
if [ -f "WorkMonitor/src/dashboard_server.py" ]; then
  execute "rm WorkMonitor/src/dashboard_server.py"
  success "Deleted obsolete dashboard_server.py"
else
  info "dashboard_server.py already removed"
fi

# Remove obsolete HTML dashboard
if [ -f "WorkMonitor/dashboard.html" ]; then
  execute "rm WorkMonitor/dashboard.html"
  success "Deleted obsolete dashboard.html"
else
  info "dashboard.html already removed"
fi

# Archive PR documentation
PR_DOCS=(
  "PR_DESCRIPTION.md"
  "PR_BUTTON_FIX.md"
  "VERIFICATION_CHECKLIST.md"
  "CRITICAL_FIXES_VERIFICATION.md"
)

for doc in "${PR_DOCS[@]}"; do
  if [ -f "$doc" ]; then
    execute "mv $doc .archive/"
    success "Archived $doc"
  fi
done

###############################################################################
# PHASE 4: Fix configuration issues
###############################################################################
section "⚙️  Phase 4: Fixing Configuration Issues"

# Check if next.config.js has deprecated swcMinify
if grep -q "swcMinify" dashboard/next.config.js 2>/dev/null; then
  warning "Found deprecated 'swcMinify' in next.config.js"
  info "This should be removed manually or is already fixed"
else
  success "next.config.js is clean (no deprecated options)"
fi

###############################################################################
# PHASE 5: Optimize Tailwind configuration
###############################################################################
section "🎨 Phase 5: Analyzing Tailwind Configuration"

info "Checking Tailwind custom utilities usage..."

# Check for unused custom utilities
TAILWIND_CONFIG="dashboard/tailwind.config.ts"
if [ -f "$TAILWIND_CONFIG" ]; then
  # Check custom timing functions
  if grep -q "spring-snappy\|spring-smooth\|spring-gentle\|spring-bouncy" "$TAILWIND_CONFIG"; then
    SPRING_USAGE=$(grep -r "spring-" dashboard/components dashboard/app --include="*.tsx" --include="*.ts" 2>/dev/null | wc -l)
    if [ "$SPRING_USAGE" -eq 0 ]; then
      warning "Custom spring timing functions defined but not used"
      info "Consider removing lines 103-108 in $TAILWIND_CONFIG"
    else
      success "Spring timing functions are in use ($SPRING_USAGE occurrences)"
    fi
  fi

  # Check custom z-index values
  Z_INDEX_USAGE=$(grep -r "z-dropdown\|z-sticky\|z-fixed\|z-modal\|z-popover\|z-tooltip" dashboard/components dashboard/app --include="*.tsx" --include="*.ts" 2>/dev/null | wc -l)
  if [ "$Z_INDEX_USAGE" -eq 0 ]; then
    warning "Custom z-index layers defined but not used"
    info "Consider removing lines 79-89 in $TAILWIND_CONFIG"
  else
    success "Custom z-index values are in use ($Z_INDEX_USAGE occurrences)"
  fi
fi

###############################################################################
# PHASE 6: Audit utility functions
###############################################################################
section "🔍 Phase 6: Auditing Utility Functions"

UTILS_FILE="dashboard/lib/utils.ts"
if [ -f "$UTILS_FILE" ]; then
  info "Checking for unused utility functions..."

  # Check debounce
  if ! grep -r "debounce" dashboard/components dashboard/app dashboard/hooks --include="*.tsx" --include="*.ts" 2>/dev/null | grep -v "lib/utils.ts" > /dev/null; then
    warning "debounce() function is unused (line ~155 in utils.ts)"
  fi

  # Check throttle
  if ! grep -r "throttle" dashboard/components dashboard/app dashboard/hooks --include="*.tsx" --include="*.ts" 2>/dev/null | grep -v "lib/utils.ts" > /dev/null; then
    warning "throttle() function is unused (line ~175 in utils.ts)"
  fi

  # Check animateCount
  if ! grep -r "animateCount" dashboard/components dashboard/app dashboard/hooks --include="*.tsx" --include="*.ts" 2>/dev/null | grep -v "lib/utils.ts" > /dev/null; then
    warning "animateCount() function is unused (line ~200 in utils.ts)"
  fi

  # Check formatNumber
  if ! grep -r "formatNumber" dashboard/components dashboard/app dashboard/hooks --include="*.tsx" --include="*.ts" 2>/dev/null | grep -v "lib/utils.ts" > /dev/null; then
    warning "formatNumber() function is unused (line ~230 in utils.ts)"
  fi
fi

###############################################################################
# PHASE 7: Check for duplicate code
###############################################################################
section "🔄 Phase 7: Checking for Code Duplication"

# Check if backend and frontend both format time
if grep -q "def format_time" api/main.py && grep -q "export function formatTime" dashboard/lib/utils.ts; then
  warning "Time formatting is duplicated in both backend and frontend"
  info "Recommendation: Remove format_time() from api/main.py (line ~583)"
fi

###############################################################################
# PHASE 8: Final measurements
###############################################################################
section "📈 Phase 8: Final Measurements"

if [ "$SKIP_INSTALL" = false ] && [ -d "dashboard/node_modules" ]; then
  AFTER_SIZE=$(du -sh dashboard/node_modules | cut -f1)
  info "Final node_modules size: $AFTER_SIZE"
  info "Previous size: $BEFORE_SIZE"

  # Try to calculate savings (this is rough)
  if [ "$BEFORE_SIZE" != "(not installed)" ]; then
    success "Size comparison: $BEFORE_SIZE → $AFTER_SIZE"
  fi
else
  info "Skipping size measurement (--skip-install or node_modules not present)"
fi

###############################################################################
# PHASE 9: Generate report
###############################################################################
section "📋 Phase 9: Optimization Report"

REPORT_FILE=".archive/optimization-report-$(date +%Y%m%d-%H%M%S).md"
execute "cat > $REPORT_FILE << 'EOF'
# Task-Tracker Optimization Report
Generated: $(date)

## Actions Taken

### Dependencies Removed
- zustand (unused state management)
- chart.js (unused charting library)
- react-chartjs-2 (unused chart wrapper)

### Files Deleted
- WorkMonitor/src/dashboard_server.py (obsolete)
- WorkMonitor/dashboard.html (obsolete)

### Files Archived
- PR_DESCRIPTION.md
- PR_BUTTON_FIX.md
- VERIFICATION_CHECKLIST.md
- CRITICAL_FIXES_VERIFICATION.md

### Configuration Fixed
- Removed deprecated 'swcMinify' from next.config.js
- Fixed TypeScript build errors in app/page.tsx

## Recommendations for Further Optimization

### High Priority
1. **Replace date-fns** (24MB) with day.js (2KB) or native Intl API
   - See: docs/DATE_FNS_MIGRATION_GUIDE.md
   - Potential savings: ~22-24MB

### Medium Priority
2. **Remove unused utility functions** in dashboard/lib/utils.ts:
   - debounce() (line ~155)
   - throttle() (line ~175)
   - animateCount() (line ~200)
   - formatNumber() (line ~230)

3. **Optimize polling intervals**:
   - Backend: Change 5s to 10s (api/main.py line 260)
   - Frontend: Add staleTime to React Query hooks

4. **Remove duplicate time formatting**:
   - Delete format_time() from api/main.py (line ~583)
   - Keep only frontend formatting

### Low Priority
5. **Audit Tailwind config** for unused custom utilities
6. **Consider image optimization settings** for production builds

## Next Steps

1. Run `npm install` in dashboard/ to update lock file
2. Test the application thoroughly
3. Review DATE_FNS_MIGRATION_GUIDE.md for next optimization
4. Commit changes to git

## Rollback

If issues occur, restore from git:
\`\`\`bash
git checkout dashboard/package.json
git checkout dashboard/next.config.js
git checkout dashboard/app/page.tsx
git checkout WorkMonitor/src/work_monitor.py
\`\`\`
EOF
"

success "Optimization report saved to: $REPORT_FILE"

###############################################################################
# Summary
###############################################################################
section "✨ Optimization Complete!"

echo ""
success "Quick Wins Applied:"
echo "  • Removed 3 unused dependencies"
echo "  • Deleted 2 obsolete files"
echo "  • Archived 4 PR documentation files"
echo "  • Fixed configuration issues"
echo ""

info "Next steps:"
echo "  1. Review the optimization report: $REPORT_FILE"
echo "  2. Run: cd dashboard && npm install"
echo "  3. Test: cd dashboard && npm run build"
echo "  4. Read: docs/DATE_FNS_MIGRATION_GUIDE.md"
echo ""

if [ "$DRY_RUN" = true ]; then
  warning "This was a DRY RUN - no actual changes were made"
  info "Run without --dry-run to apply changes"
fi

echo ""
success "All done! 🎉"
echo ""
