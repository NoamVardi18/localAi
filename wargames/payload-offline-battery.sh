#!/bin/bash
# Offline privacy battery for the localai wargame (00-localai-stack.md M9).
# MUST run as a detached script: the Claude Code executor itself dies without
# network, so it launches this, waits ~3 min, and reads the results file after
# wifi returns. Usage:
#   bash payload-offline-battery.sh <daily_model> <embed_model>        # real run
#   DRYRUN=1 bash payload-offline-battery.sh <daily_model> <embed_model>  # skip wifi toggle (logic test)
set -u
DAILY="${1:?daily model tag required}"
EMBED="${2:?embed model tag required}"
OUT="$HOME/Claude/localai/wargames/answers/offline-battery.txt"
mkdir -p "$(dirname "$OUT")"
: > "$OUT"
log() { echo "$(date +%H:%M:%S) $*" >> "$OUT"; }

log "START daily=$DAILY embed=$EMBED dryrun=${DRYRUN:-0}"

if [ "${DRYRUN:-0}" != "1" ]; then
  networksetup -setairportpower en0 off
  sleep 5
  if ping -c1 -t3 1.1.1.1 >/dev/null 2>&1; then
    log "FAIL-SETUP network still reachable after wifi off (ethernet/tether?) — battery invalid"
  else
    log "OK offline confirmed (ping 1.1.1.1 failed as expected)"
  fi
fi

# 1. generation while offline
GEN=$(curl -s --max-time 300 http://127.0.0.1:11434/api/generate \
  -d "{\"model\":\"$DAILY\",\"prompt\":\"Reply with exactly: OFFLINE-GEN-OK\",\"stream\":false}")
echo "$GEN" | grep -q "OFFLINE-GEN-OK" && log "OK offline generation" \
  || log "FAIL offline generation: $(echo "$GEN" | head -c 300)"
TOKS=$(echo "$GEN" | /usr/bin/python3 -c 'import json,sys;d=json.load(sys.stdin);print(round(d["eval_count"]/d["eval_duration"]*1e9,1))' 2>/dev/null)
log "offline gen tok/s: ${TOKS:-n/a}"

# 2. embedding while offline
EMB=$(curl -s --max-time 120 http://127.0.0.1:11434/api/embed \
  -d "{\"model\":\"$EMBED\",\"input\":\"בדיקת הטמעה במצב לא מקוון\"}")
echo "$EMB" | grep -q '"embeddings":\[\[' && log "OK offline embedding" \
  || log "FAIL offline embedding: $(echo "$EMB" | head -c 300)"

# 3. what is ollama listening on / connected to
lsof -i -P -n 2>/dev/null | grep -i ollama >> "$OUT" || log "note: no ollama lines in lsof -i"
NONLOCAL=$(lsof -i -P -n 2>/dev/null | grep -i ollama | grep -v '127.0.0.1\|\[::1\]\|LISTEN' || true)
[ -z "$NONLOCAL" ] && log "OK no non-localhost ollama connections" \
  || log "FAIL non-localhost ollama connection seen: $NONLOCAL"

if [ "${DRYRUN:-0}" != "1" ]; then
  networksetup -setairportpower en0 on
  for i in $(seq 1 24); do
    ping -c1 -t3 1.1.1.1 >/dev/null 2>&1 && { log "OK wifi restored (${i}x5s)"; break; }
    sleep 5
  done
  ping -c1 -t3 1.1.1.1 >/dev/null 2>&1 || log "WARN wifi NOT back after 120s — turn it on manually"
fi
log "END battery done"
