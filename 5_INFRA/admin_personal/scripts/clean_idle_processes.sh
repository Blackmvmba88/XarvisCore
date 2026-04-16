#!/usr/bin/env bash
# clean_idle_processes.sh
# Safe helper to identify candidate processes of the current user that are (likely) idle
# and offer to terminate them in order to free memory.
# IMPORTANT: by default only inspects processes owned by the current user to avoid
# killing system processes.

set -euo pipefail
USER_ONLY=true
DRY_RUN=false
FORCE=false
CPU_THRESHOLD=0.1   # percent
RSS_THRESHOLD_MB=200
AGE_SECONDS=3600    # process elapsed time > 1 hour

usage(){
  cat <<EOF
Usage: $0 [--dry-run] [--force] [--cpu N] [--rss N] [--age SECONDS]
Options:
  --dry-run     Show candidates but don't kill anything
  --force       Kill candidates without asking (use with care)
  --cpu N       Max CPU% to consider idle (default ${CPU_THRESHOLD})
  --rss N       Min RSS (MB) to consider big process (default ${RSS_THRESHOLD_MB})
  --age N       Min elapsed seconds (default ${AGE_SECONDS})
EOF
}

while [[ ${#} -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=true; shift;;
    --force) FORCE=true; shift;;
    --cpu) CPU_THRESHOLD="$2"; shift 2;;
    --rss) RSS_THRESHOLD_MB="$2"; shift 2;;
    --age) AGE_SECONDS="$2"; shift 2;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg: $1"; usage; exit 1;;
  esac
done

echo "[info] Running with cpu<${CPU_THRESHOLD}% rss>${RSS_THRESHOLD_MB}MB age>${AGE_SECONDS}s  dry-run=${DRY_RUN} force=${FORCE}"

# Show memory status
if command -v vm_stat >/dev/null 2>&1; then
  echo "\n--- vm_stat summary ---"
  vm_stat | sed -n '1,8p'
  echo "-----------------------\n"
fi

# Fetch candidate processes owned by current user
# Columns: pid,pcpu,rss_kb,etime,comm
ps -u "$USER" -axo pid,pcpu,rss,etime,comm --no-headers | \
  awk -v cpu="${CPU_THRESHOLD}" -v rssMB="${RSS_THRESHOLD_MB}" -v age="${AGE_SECONDS}" '{ 
    pid=$1; cpuv=$2; rsskb=$3; etime=$4; cmd=$5;
    rssmb=(rsskb/1024);
    # Convert etime to seconds approx: [[dd-]HH:]MM:SS
    split(etime,a,":"); s=0; if (length(a)==3) { s = a[1]*3600 + a[2]*60 + a[3]; } else if (length(a)==2) { s = a[1]*60 + a[2]; } else { s = 0; }
    if (cpuv+0 <= cpu && rssmb+0 >= rssMB && s >= age) print pid, cpuv, rssmb, s, cmd; }' \
  | while read -r pid pcpu rssmb secs cmd; do
    # skip if pid is empty
    [[ -z "$pid" ]] && continue
    # extra safety: ensure process is actually owned by current user
    owner=$(ps -p "$pid" -o user= 2>/dev/null | tr -d ' ')
    if [[ "$owner" != "$USER" ]]; then
      continue
    fi

    printf "\nCandidate: PID=%s  CPU=%.2f%%  RSS=%.0fMB  AGE=%ds  CMD=%s\n" "$pid" "$pcpu" "$rssmb" "$secs" "$cmd"

    if [[ "$DRY_RUN" == "true" ]]; then
      continue
    fi

    if [[ "$FORCE" == "true" ]]; then
      echo "Killing PID $pid (SIGTERM)..."
      kill "$pid" || echo "Failed to send SIGTERM to $pid"
      sleep 2
      if kill -0 "$pid" 2>/dev/null; then
        echo "Sending SIGKILL to $pid"
        kill -9 "$pid" || true
      fi
      continue
    fi

    # Ask for confirmation
    read -r -p "Kill PID $pid? (y/N) " ans
    case "$ans" in
      [yY]|[yY][eE][sS])
        echo "Killing PID $pid (SIGTERM)..."
        kill "$pid" || echo "Failed to send SIGTERM to $pid"
        sleep 2
        if kill -0 "$pid" 2>/dev/null; then
          echo "Sending SIGKILL to $pid"
          kill -9 "$pid" || true
        fi
        ;;
      *) echo "Skipped PID $pid";;
    esac
  done

# Show memory summary after (best-effort)
if command -v vm_stat >/dev/null 2>&1; then
  echo "\n--- vm_stat summary (after) ---"
  vm_stat | sed -n '1,8p'
  echo "-------------------------------\n"
fi

echo "Done. Review above and repeat for additional cleanup if needed."
