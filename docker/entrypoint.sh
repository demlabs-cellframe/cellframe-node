#!/bin/bash
# Cellframe Node container entrypoint.
# First run: populate /opt/cellframe-node/{etc,share} from the pristine
# templates baked into the image, generate cellframe-node.cfg, enable the
# networks listed in $CELLFRAME_NETWORKS. Later runs: leave an existing
# configuration completely alone.
set -e

BASE="${BASE:-/opt/cellframe-node}"
TPL="${TPL_DIR:-$BASE/share.tpl}"
TPL_SHARE="${TPL_SHARE:-$TPL/dist/share}"
TPL_ETC="${TPL_ETC:-$TPL/etc}"
CFG="$BASE/etc/cellframe-node.cfg"

log() { echo "[entrypoint] $*"; }

mkdir -p "$BASE/var/lib/global_db" "$BASE/var/lib/wallet" "$BASE/var/lib/plugins" \
         "$BASE/var/lib/ca" "$BASE/var/log" "$BASE/var/run" "$BASE/tmp" \
         "$BASE/etc/network" "$BASE/etc/cellframe-node.cfg.d" "$BASE/etc/patches.d"

# Runtime share data (CA bundle, RPC docs) from the pristine copy.
if [ ! -d "$BASE/share/ca" ]; then
    mkdir -p "$BASE/share"
    cp -a "$TPL_SHARE/ca"      "$BASE/share/ca"
    cp -a "$TPL_SHARE/docs"    "$BASE/share/docs"
    cp -a "$TPL_SHARE/configs" "$BASE/share/configs"
    cp -a "$TPL_SHARE/default.setup" "$BASE/share/default.setup" 2>/dev/null || true
    cp -a "$TPL_SHARE/confctl.sh"    "$BASE/share/confctl.sh"    2>/dev/null || true
    log "populated share/ from templates"
fi

# Main config: generate once, never overwrite.
if [ ! -f "$CFG" ]; then
    cp "$TPL_SHARE/configs/cellframe-node.cfg" "$CFG"

    # Explicit CLI listener so `cellframe-node-cli` and the /health check work
    # the same way in every deployment (the template ships it commented out).
    # Inside a container the address must be 0.0.0.0 - docker port publishing
    # cannot reach a loopback-only bind; exposure is controlled host-side by
    # what gets published (-p 127.0.0.1:12345:12345 keeps it private).
    if grep -q '^#listen-address=\[127.0.0.1:12345\]' "$CFG"; then
        sed -i 's|^#listen-address=\[127.0.0.1:12345\]|listen-address=0.0.0.0:12345|' "$CFG"
    else
        printf '\nlisten-address=0.0.0.0:12345\n' >> "$CFG"
    fi

    # The shipped template still carries verbose per-request DEX logging;
    # production nodes should not pay the I/O cost (code default is now false,
    # keep the generated config explicit and quiet too).
    sed -i 's|^\[srv_dex\]$|[srv_dex]\ndebug_more=false|' "$CFG"

    if [ "${CELLFRAME_DEBUG_MODE:-false}" = "true" ]; then
        sed -i 's|^debug_mode=.*|debug_mode=true|' "$CFG"
    fi

    log "generated $CFG"
fi

# Networks: template share/configs/network/<Net>.cfg -> etc/network/<Net>.cfg
# (an enabled net is a plain .cfg, a disabled one is .cfg.dis), plus the
# per-chain templates from dist/etc/network/<Net>/.
IFS=',' ; for NET in ${CELLFRAME_NETWORKS:-Backbone} ; do
    NET="$(echo "$NET" | tr -d ' ')"
    [ -z "$NET" ] && continue
    if [ -f "$TPL_SHARE/configs/network/$NET.cfg" ] && [ ! -f "$BASE/etc/network/$NET.cfg" ]; then
        cp "$TPL_SHARE/configs/network/$NET.cfg" "$BASE/etc/network/$NET.cfg"
        # The shipped template leaves the role to the deployer; the node refuses
        # to create the net while it is empty. Default to a full (syncing) node,
        # overridable per deployment.
        sed -i "s|^node-role=.*|node-role=${CELLFRAME_NODE_ROLE:-full}|" "$BASE/etc/network/$NET.cfg"
        log "enabled network $NET (role ${CELLFRAME_NODE_ROLE:-full})"
    fi
    if [ -d "$TPL_ETC/network/$NET" ] && [ ! -d "$BASE/etc/network/$NET" ]; then
        mkdir -p "$BASE/etc/network/$NET"
        cp -a "$TPL_ETC/network/$NET/." "$BASE/etc/network/$NET/"
        log "installed chain templates for $NET"
    fi
done ; unset IFS

# Config overlays, no base-file edits:
#  - etc/cellframe-node.cfg.d/*.cfg are merged natively by dap_config
#    (alphasorted; later files override earlier keys);
#  - etc/patches.d/*.cfg are applied by copying into cfg.d at startup
#    (same-name file replaces the previous copy), matching the confctl
#    patches.d workflow. Both dirs live in the mountable etc volume.
if [ -d "$BASE/etc/patches.d" ]; then
    for PATCH in "$BASE/etc/patches.d/"*.cfg ; do
        [ -f "$PATCH" ] || continue
        cp -f "$PATCH" "$BASE/etc/cellframe-node.cfg.d/"
        log "applied config patch $(basename "$PATCH")"
    done
fi
if [ ! -f "$BASE/etc/cellframe-node.cfg.d/README.txt" ]; then
    cat > "$BASE/etc/cellframe-node.cfg.d/README.txt" <<'EOT'
Drop-in config fragments (*.cfg) placed here are merged into the node
configuration on start (alphasorted file order; later keys override).
Prefer these over editing the base cellframe-node.cfg - the base is
regenerated here on first run only.
EOT
fi

log "starting: $*"
exec "$@"
