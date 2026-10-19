#!/usr/bin/env bash
# Ledger-state equivalence runner (stage 5 of the state-persistence plan).
#
# Captures a canonical fingerprint of the ledger/chain/service state a running
# node reports, so three starts can be compared:
#   (a) full scan, no snapshot;
#   (b) snapshot restore, snapshot_full_apply=false (safe mode);
#   (c) snapshot restore, snapshot_full_apply=true  (service replay suppressed).
#
# Usage:
#   tools/ledger-equivalence-check.sh capture <label>
#   tools/ledger-equivalence-check.sh compare <label-a> <label-b>
#
# Environment:
#   CF_CLI      cellframe-node-cli binary   (default: cellframe-node-cli)
#   CF_CLI_ARGS extra CLI arguments         (default: empty, CLI defaults to 127.0.0.1:12345)
#   CF_NET      network name                (default: Backbone)
#   CF_CHAIN    chain name                  (default: main)
#   CF_EQ_OUT   output directory            (default: <repo>/equivalence-output)
#   CF_ADDR     address for the wallet-outputs probe (optional)
#   CF_TOKEN    token ticker for that probe (default: CELL)
#
# The fingerprint is line-sorted: ledger hash-table iteration order is not
# semantic, and every number that is a timestamp/age is normalized out.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLI="${CF_CLI:-cellframe-node-cli}"
CLI_ARGS="${CF_CLI_ARGS:-}"
NET="${CF_NET:-Backbone}"
CHAIN="${CF_CHAIN:-main}"
OUT_ROOT="${CF_EQ_OUT:-$ROOT_DIR/equivalence-output}"
ADDR="${CF_ADDR:-}"
TOKEN="${CF_TOKEN:-CELL}"

if command -v sha256sum >/dev/null 2>&1; then
    SHA256="sha256sum"
else
    SHA256="shasum -a 256"   # macOS
fi

cmds() {
    printf '%s\n' \
        "tx_history -count -net $NET" \
        "token list -net $NET -full" \
        "ledger list balance -net $NET -limit 1000000" \
        "ledger event key list -net $NET" \
        "ledger event list -net $NET" \
        "poll list -net $NET" \
        "srv_stake list keys -net $NET" \
        "srv_stake list tx -net $NET" \
        "chain cache show -net $NET -chain $CHAIN"
    if [ -n "$ADDR" ]; then
        printf '%s\n' "wallet outputs -net $NET -token $TOKEN -addr $ADDR"
    fi
}

normalize() {
    # The sidecar line carries a save age and absolute paths; both vary between
    # captures on purpose. Everything else must match byte for byte.
    sed -E -e 's/age [0-9]+ s/age N s/g' \
           -e 's#/[^ ]*/ledger-snapshot\.bin#[snapshot]#g' \
           -e 's#/[^ ]*\.dchaincell\.state#[sidecar]#g' \
        | LC_ALL=C sort
}

run_cmd() { # <command line> -> stdout+stderr, exit code appended as a marker
    local l_cmd="$1" l_rc=0 l_out
    # The CLI reads commands from stdin and connects to its default port.
    l_out="$(printf '%s\nquit\n' "$l_cmd" | $CLI $CLI_ARGS 2>&1)" || l_rc=$?
    printf '%s\n' "$l_out" | normalize
    printf 'exit_code: %d\n' "$l_rc"
}

capture() {
    local l_label="$1" l_dir="$OUT_ROOT/$1" l_i=0
    mkdir -p "$l_dir"
    : > "$l_dir/state.txt"
    while IFS= read -r l_cmd; do
        l_i=$((l_i + 1))
        {
            printf '=== %s ===\n' "$l_cmd"
            run_cmd "$l_cmd"
            printf '\n'
        } >> "$l_dir/state.txt"
        printf '[%02d] %s\n' "$l_i" "$l_cmd"
    done < <(cmds)
    {
        printf '=== version ===\n'
        run_cmd "version"
    } >> "$l_dir/state.txt"

    # Per-command digests: a differing line in compare() names the command.
    awk '/^=== .* ===$/ { cmd=$0; next } { print cmd "\t" $0 }' "$l_dir/state.txt" \
        | LC_ALL=C sort > "$l_dir/state.sorted"
    LC_ALL=C sort "$l_dir/state.sorted" | $SHA256 | awk '{ print $1 }' > "$l_dir/fingerprint.txt"
    printf 'captured %s: %s\n' "$l_label" "$(cat "$l_dir/fingerprint.txt")"
}

compare() {
    local l_a="$1" l_b="$2"
    local l_fa="$OUT_ROOT/$l_a/fingerprint.txt" l_fb="$OUT_ROOT/$l_b/fingerprint.txt"
    [ -f "$l_fa" ] || { echo "missing $l_fa" >&2; exit 2; }
    [ -f "$l_fb" ] || { echo "missing $l_fb" >&2; exit 2; }
    if cmp -s "$l_fa" "$l_fb"; then
        echo "EQUIVALENT: $l_a == $l_b ($(cat "$l_fa"))"
        return 0
    fi
    echo "DIFFERENT: $l_a != $l_b"
    echo "--- per-command diff (first 200 lines) ---"
    diff -u "$OUT_ROOT/$l_a/state.sorted" "$OUT_ROOT/$l_b/state.sorted" | head -200 || true
    return 1
}

case "${1:-}" in
    capture)
        [ -n "${2:-}" ] || { echo "usage: $0 capture <label>" >&2; exit 2; }
        capture "$2"
        ;;
    compare)
        [ -n "${2:-}" ] && [ -n "${3:-}" ] || { echo "usage: $0 compare <label-a> <label-b>" >&2; exit 2; }
        compare "$2" "$3"
        ;;
    *)
        sed -n '2,20p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
        exit 2
        ;;
esac
