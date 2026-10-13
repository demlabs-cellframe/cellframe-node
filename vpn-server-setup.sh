#!/usr/bin/env bash
# Linux host networking setup. Plugin/network identity is not guessed or changed.
set -Eeuo pipefail
trap 'rc=$?; printf "ERROR host=%s line=%s command=%s exit=%s\n" "$(hostname)" "$LINENO" "$BASH_COMMAND" "$rc" >&2; exit "$rc"' ERR
VPN_SUBNET="${VPN_SUBNET:-10.11.12.0/24}"
VPN_GW="${VPN_GW:-10.11.12.1}"
TUN_IF="${TUN_IF:-tun0}"
DNS_MODE="${DNS_MODE:-plugin}"
DNS_UPSTREAM="${DNS_UPSTREAM:-1.1.1.1,8.8.8.8}"
printf '=== VPN setup: host=%s label=%s UTC=%s ===\n' "$(hostname)" "${SERVER_LABEL:-$(hostname)}" "$(date -u +%FT%TZ)"
[[ $EUID == 0 ]] || { printf 'ERROR: run with sudo\n' >&2; exit 2; }
for cmd in ip iptables sysctl install systemctl; do
    command -v "$cmd" >/dev/null || { printf 'ERROR: missing %s\n' "$cmd" >&2; exit 2; }
done
WAN_IF="${WAN_IF:-$(ip -4 route show default | awk 'NR==1 {for(i=1;i<=NF;i++) if($i=="dev") print $(i+1)}')}"
[[ -n "$WAN_IF" ]] || { printf 'ERROR: no WAN interface; set WAN_IF\n' >&2; exit 2; }
[[ "$WAN_IF" =~ ^[a-zA-Z0-9_.:-]+$ && "$TUN_IF" =~ ^[a-zA-Z0-9_.:-]+$ && "$VPN_SUBNET" =~ ^[0-9.]+/[0-9]+$ ]] || { printf 'ERROR: invalid interface/subnet syntax\n' >&2; exit 2; }
case "$DNS_MODE" in plugin|external) ;; dnsmasq) command -v dnsmasq >/dev/null || { printf 'ERROR: install dnsmasq using your package manager, then rerun\n' >&2; exit 2; };; *) printf 'ERROR: DNS_MODE must be plugin, external or dnsmasq\n' >&2; exit 2;; esac
ip link show dev "$WAN_IF"
printf 'WAN=%s TUN=%s VPN=%s DNS_MODE=%s\n' "$WAN_IF" "$TUN_IF" "$VPN_SUBNET" "$DNS_MODE"
[[ -c /dev/net/tun ]] || modprobe tun
[[ -c /dev/net/tun ]] || { printf 'ERROR: /dev/net/tun unavailable; check host/container permissions\n' >&2; exit 1; }
install -d /etc/sysctl.d
printf 'net.ipv4.ip_forward=1\n' > /etc/sysctl.d/90-cellframe-vpn.conf
sysctl -p /etc/sysctl.d/90-cellframe-vpn.conf

# Restore only our rules, never a snapshot of unrelated host firewall tables.
IPTABLES=$(command -v iptables)
install -d /usr/local/sbin
RULES=/usr/local/sbin/cellframe-vpn-firewall
if [[ -f "$RULES" ]]; then cp -p "$RULES" "$RULES.bak"; fi
cat > "$RULES" <<EOF
#!/usr/bin/env bash
set -Eeuo pipefail
IPTABLES='$IPTABLES'
VPN_SUBNET='$VPN_SUBNET'
WAN_IF='$WAN_IF'
TUN_IF='$TUN_IF'
EOF
cat >> "$RULES" <<'EOF'
ensure_rule() {
    local table=$1 chain=$2; shift 2
    "$IPTABLES" -w 5 -t "$table" -S "$chain" >/dev/null
    if ! "$IPTABLES" -w 5 -t "$table" -C "$chain" "$@" 2>/dev/null; then
        "$IPTABLES" -w 5 -t "$table" -A "$chain" "$@"
    fi
}
ensure_rule nat POSTROUTING -s "$VPN_SUBNET" -o "$WAN_IF" -j MASQUERADE
ensure_rule filter FORWARD -i "$TUN_IF" -s "$VPN_SUBNET" -o "$WAN_IF" -j ACCEPT
ensure_rule filter FORWARD -i "$WAN_IF" -o "$TUN_IF" -d "$VPN_SUBNET" -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
ensure_rule mangle FORWARD -i "$TUN_IF" -s "$VPN_SUBNET" -o "$WAN_IF" -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu
ensure_rule mangle FORWARD -i "$WAN_IF" -o "$TUN_IF" -d "$VPN_SUBNET" -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu
EOF
chmod 755 "$RULES"
install -d /etc/systemd/system
cat > /etc/systemd/system/cellframe-vpn-firewall.service <<'EOF'
[Unit]
Description=Ensure Cellframe VPN forwarding rules
After=network.target
Before=cellframe-node.service
[Service]
Type=oneshot
ExecStart=/usr/local/sbin/cellframe-vpn-firewall
RemainAfterExit=yes
[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable cellframe-vpn-firewall.service
systemctl restart cellframe-vpn-firewall.service
printf 'NOTE: rules are appended; inspect earlier DROP rules and cloud firewall. Old vpn-iptables.service, if present, must be reviewed separately.\n'

if [[ "$DNS_MODE" == dnsmasq ]]; then
    [[ "$VPN_GW" =~ ^[0-9.]+$ ]] || { printf 'ERROR: invalid VPN_GW\n' >&2; exit 2; }
    install -d /etc/dnsmasq.d
    [[ ! -f /etc/dnsmasq.d/vpn.conf ]] || cp -p /etc/dnsmasq.d/vpn.conf /etc/dnsmasq.d/vpn.conf.bak
    {
        printf 'listen-address=%s\nbind-dynamic\nno-resolv\ncache-size=1000\n' "$VPN_GW"
        IFS=',' read -ra resolvers <<< "$DNS_UPSTREAM"
        for resolver in "${resolvers[@]}"; do
            [[ "$resolver" =~ ^[0-9a-fA-F:.]+$ ]] || { printf 'ERROR: invalid DNS address\n' >&2; exit 2; }
            printf 'server=%s\n' "$resolver"
        done
    } > /etc/dnsmasq.d/vpn.conf
    dnsmasq --test
    systemctl enable dnsmasq
    systemctl restart dnsmasq
fi
printf 'Host networking configured. No node/plugin config was modified.\n'
printf 'Free VPN requires srv-vpn.cfg: enabled=true, allow_free_srv=true; current SDK also requires a resolvable [srv_vpn] net in node config (Offline allowed).\n'
printf 'Next: sudo ./vpn-server-check.sh. This script does not prove VPN service initialization or external port reachability.\n'
