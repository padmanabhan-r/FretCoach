#!/usr/bin/env bash
set -e

MODE=${1:-dry}   # default = dry-run

# rsync flags:
# -a  archive
# -v  verbose (needed for itemized output)
# --delete remove files not in source
# --itemize-changes show only real diffs
# --ignore-times ignore timestamp-only changes
RSYNC_FLAGS="-av --delete --itemize-changes --ignore-times"

if [[ "$MODE" == "dry" ]]; then
  echo "🧪 DRY-RUN MODE (no files will be changed)"
  RSYNC_FLAGS="$RSYNC_FLAGS --dry-run"
elif [[ "$MODE" == "apply" ]]; then
  echo "🚀 APPLY MODE (files WILL be changed)"
else
  echo "❌ Unknown mode: $MODE"
  echo "Usage: ./sync-web.sh [dry|apply]"
  exit 1
fi

echo "=============================="
echo " Syncing FretCoach Web Assets "
echo "=============================="

BASE="/Users/paddy/Documents/Github/FretCoach"

BACKEND_SRC="$BASE/web/web-backend/"
BACKEND_DEST="/Users/paddy/Documents/Github/FretCoach-Web-Backend/"

FRONTEND_SRC="$BASE/web/web-frontend/"
FRONTEND_DEST="/Users/paddy/Documents/Github/FretCoach-Web-Frontend/"

COMMON_EXCLUDES=(
  --exclude '.git'
  --exclude '.git/**'
  --exclude '.DS_Store'
  --exclude '__pycache__'
  --exclude '*.pyc'
  --exclude '.env'
  --exclude '.env.*'
)

echo ""
echo "▶ WEB BACKEND changes:"
rsync $RSYNC_FLAGS \
  "${COMMON_EXCLUDES[@]}" \
  "$BACKEND_SRC" "$BACKEND_DEST" \
  | grep -E '^[><].*([+s])|\*deleting' || echo "✔ No backend changes"

echo ""
echo "▶ WEB FRONTEND changes:"
rsync $RSYNC_FLAGS \
  "${COMMON_EXCLUDES[@]}" \
  --exclude 'node_modules' \
  --exclude 'dist' \
  "$FRONTEND_SRC" "$FRONTEND_DEST" \
  | grep -E '^[><].*([+s])|\*deleting' || echo "✔ No frontend changes"

echo ""
echo "✅ Sync completed ($MODE mode)"
