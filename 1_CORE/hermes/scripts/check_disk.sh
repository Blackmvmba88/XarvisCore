#!/usr/bin/env bash
set -euo pipefail
# check_disk.sh — exit 0 if free GiB >= threshold
THRESHOLD_GIB="${1:-15}"
FREE_KB=$(df -k . | tail -1 | awk '{print $4}')
FREE_GIB=$((FREE_KB/1024/1024))
if [ "$FREE_GIB" -lt "$THRESHOLD_GIB" ]; then
  echo "FREE_GIB=${FREE_GIB} < THRESHOLD_GIB=${THRESHOLD_GIB}"
  exit 1
fi
echo "FREE_GIB=${FREE_GIB} >= THRESHOLD_GIB=${THRESHOLD_GIB}"
