#!/usr/bin/env bash
# Polls Backbone sync progress and returns as soon as the condition holds.
# Usage: tools/wait-sync.sh <ssh-target> <chain> <condition> [timeout_s] [interval_s]
#   condition: synced | online | progress | advanced
# Prints only changed samples; exits 0 when the condition holds, 2 on timeout.
set -uo pipefail
TARGET="$1"; CHAIN="${2:-main}"; MODE="${3:-synced}"
TIMEOUT="${4:-5400}"; INTERVAL="${5:-45}"
CLI="/opt/cellframe-node/bin/cellframe-node-cli net get status -net Backbone"
deadline=$(( $(date +%s) + TIMEOUT ))
first=""; last_print=""
while [ "$(date +%s)" -lt "$deadline" ]; do
    sample=$(ssh -o BatchMode=yes -o ConnectTimeout=15 -l root "$TARGET" "$CLI" 2>/dev/null \
        | python3 -c '
import sys, re
chain = sys.argv[1]
cur = net = 0; state = "?"
lines = sys.stdin.read().splitlines()
for i, l in enumerate(lines):
    if re.match(r"\s*%s:\s*$" % re.escape(chain), l):
        for l2 in lines[i+1:i+6]:
            m = re.match(r"\s*current:\s*(\d+)", l2)
            if m: cur = int(m.group(1))
            m = re.match(r"\s*in network:\s*(\d+)", l2)
            if m: net = int(m.group(1))
    m = re.match(r"\s*current:\s*(NET_STATE_\w+)", l)
    if m: state = m.group(1)
print("%d/%d %s" % (cur, net, state))
' "$CHAIN") || { sleep "$INTERVAL"; continue; }
    cur=${sample%%/*}; rest=${sample#*/}; net=${rest%% *}; state=${sample##* }
    [ -z "$first" ] && first="$cur"
    case "$MODE" in
        synced)   { [ "$state" = "NET_STATE_ONLINE" ] || { [ "$net" -gt 0 ] && [ "$cur" -ge "$net" ]; }; } && { echo "$CHAIN synced: $sample"; exit 0; } ;;
        online)   [ "$state" = "NET_STATE_ONLINE" ] && { echo "online: $CHAIN $sample"; exit 0; } ;;
        progress) [ "$cur" != "$first" ] && { echo "progress: $first -> $sample"; exit 0; } ;;
        advanced) [ "$cur" -gt "${first:-0}" ] 2>/dev/null && { echo "advanced: $first -> $sample"; exit 0; } ;;
    esac
    [ "$sample" != "$last_print" ] && { echo "$(date +%H:%M:%S) $CHAIN $sample"; last_print="$sample"; }
    sleep "$INTERVAL"
done
echo "TIMEOUT ${TIMEOUT}s: last $last_print (started $first)"; exit 2
