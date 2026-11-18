#!/usr/bin/env bash
# RPC load profile for the [rpc-server] plain JSON-RPC listener.
#
# Sends a rotating mix of read-only commands (net version, block list, block
# dump, tx_history, wallet outputs) at a fixed request rate and reports latency
# percentiles and HTTP status counts. This is the stage-5 acceptance profile:
# 20 RPS for an hour, p95 net/version < 300 ms, wallet outputs cache-hit < 500 ms,
# tx_history < 2 s, timeouts/5xx < 0.1%.
#
# Usage:
#   tools/rpc-load-profile.sh [url] [duration_sec] [rps] [workers]
#
# Defaults: http://127.0.0.1:12400/rpc 3600 20 8
#
# Environment:
#   CF_NET, CF_CHAIN, CF_TOKEN  request parameters (default Backbone/main/CELL)
#   CF_ADDR                     address for wallet outputs (otherwise that probe is skipped)
#   CF_BLOCK_NUM                fixed block number for block dump (default: 100000)
#   CF_OUT                      report/latency directory (default: <repo>/rpc-load-output)
#   CF_CURL_OPTS                extra curl options
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
URL="${1:-http://127.0.0.1:12400/rpc}"
DURATION="${2:-3600}"
RPS="${3:-20}"
WORKERS="${4:-8}"
NET="${CF_NET:-Backbone}"
CHAIN="${CF_CHAIN:-main}"
TOKEN="${CF_TOKEN:-CELL}"
ADDR="${CF_ADDR:-}"
BLOCK_NUM="${CF_BLOCK_NUM:-100000}"
OUT_DIR="${CF_OUT:-$ROOT_DIR/rpc-load-output}"
CURL_OPTS="${CF_CURL_OPTS:-}"

mkdir -p "$OUT_DIR"
RUN_DIR="$OUT_DIR/run-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$RUN_DIR"

# The wire format is one semicolon-separated command line in params[0].
build_body() { # <command line>
    local l_cmd="$1"
    printf '{"jsonrpc":"2.0","method":"%s","params":["%s"],"id":1}' \
        "${l_cmd%% *}" "$l_cmd"
}

CMDS=(
    "net;version"
    "block;last;-net;$NET;-chain;$CHAIN"
    "block;list;-net;$NET;-chain;$CHAIN;-limit;20"
    "block;dump;-net;$NET;-chain;$CHAIN;-num;$BLOCK_NUM"
    "tx_history;-all;-net;$NET;-limit;20"
)
if [ -n "$ADDR" ]; then
    CMDS+=("wallet;outputs;-net;$NET;-chain;$CHAIN;-token;$TOKEN;-addr;$ADDR")
fi

N_CMDS=${#CMDS[@]}
PER_WORKER=$(awk -v r="$RPS" -v w="$WORKERS" 'BEGIN { printf "%.4f", r / w }')
END_TS=$(( $(date +%s) + DURATION ))
# Each worker sleeps between requests; the aggregate rate is RPS.
INTERVAL=$(awk -v r="$PER_WORKER" 'BEGIN { if (r > 0) printf "%.4f", 1 / r; else print "0" }')

worker() { # <worker-id>
    local l_id="$1" l_idx=$(( $1 % N_CMDS )) l_file="$RUN_DIR/worker-$1.csv"
    : > "$l_file"
    while [ "$(date +%s)" -lt "$END_TS" ]; do
        local l_cmd="${CMDS[$l_idx]}"
        local l_body
        l_body="$(build_body "$l_cmd")"
        # One line per request: status, time_total, size, command index.
        local l_res
        l_res=$(curl -sS -o /dev/null $CURL_OPTS -m 10 \
            -H 'Content-Type: application/json' \
            -w '%{http_code}\t%{time_total}\t%{size_download}\t%{time_namelookup}' \
            -d "$l_body" "$URL" 2>>"$RUN_DIR/curl-errors.log") || l_res=$'000\t0\t0\t0'
        printf '%d\t%s\t%s\n' "$l_idx" "$l_res" >> "$l_file"
        l_idx=$(( (l_idx + 1) % N_CMDS ))
        sleep "$INTERVAL"
    done
}

echo "RPC load: $URL, ${DURATION}s, ${RPS} RPS, ${WORKERS} workers, ${N_CMDS} commands"
echo "report:  $RUN_DIR"
pids=()
for i in $(seq 0 $((WORKERS - 1))); do
    worker "$i" &
    pids+=($!)
done
trap 'kill "${pids[@]}" 2>/dev/null || true' INT TERM
wait "${pids[@]}" 2>/dev/null || true

cat "$RUN_DIR"/worker-*.csv > "$RUN_DIR/all.csv"
cut -f3 "$RUN_DIR/all.csv" | sort -n > "$RUN_DIR/lat.sorted"
N=$(wc -l < "$RUN_DIR/lat.sorted" | tr -d ' ')
pick() { sed -n "$1p" "$RUN_DIR/lat.sorted"; }
{
    echo "requests: $N"
    if [ "$N" -gt 0 ]; then
        echo "p50: $(pick $(( N * 50 / 100 ))) s"
        echo "p95: $(pick $(( N * 95 / 100 ))) s"
        echo "p99: $(pick $(( N * 99 / 100 ))) s"
        echo "max: $(tail -1 "$RUN_DIR/lat.sorted") s"
    fi
    echo "HTTP status counts:"
    cut -f2 "$RUN_DIR/all.csv" | sort | uniq -c
    ERR=$(awk -F '\t' '$2 == "000"' "$RUN_DIR/all.csv" | wc -l | tr -d ' ')
    FIVE=$(awk -F '\t' '$2 ~ /^5/' "$RUN_DIR/all.csv" | wc -l | tr -d ' ')
    if [ "$N" -gt 0 ]; then
        awk -v e="$ERR" -v f="$FIVE" -v n="$N" 'BEGIN {
            printf "errors(000): %d (%.3f%%)\n", e, 100.0 * e / n
            printf "5xx: %d (%.3f%%)\n", f, 100.0 * f / n
        }'
    fi
} | tee "$RUN_DIR/report.txt"
