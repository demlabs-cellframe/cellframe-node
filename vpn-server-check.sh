#!/usr/bin/env bash
# Read-only Linux VPN diagnostics. Exit 1 = failed checks, 2 = missing prerequisite.
set -u
VPN_SUBNET="${VPN_SUBNET:-10.11.12.0/24}"
VPN_GW="${VPN_GW:-10.11.12.1}"
TUN_IF="${TUN_IF:-tun0}"
NODE_CFG="${NODE_CFG:-/opt/cellframe-node/etc/cellframe-node.cfg}"
PLUGIN_CFG="${PLUGIN_CFG:-/opt/cellframe-node/var/lib/plugins/srv-vpn/srv-vpn.cfg}"
DNS_MODE="${DNS_MODE:-plugin}"
FAILURES=0
ok() { printf 'PASS %s\n' "$*"; }
fail() { printf 'FAIL %s\n' "$*" >&2; FAILURES=$((FAILURES+1)); }
warn() { printf 'WARN %s\n' "$*"; }
cfg() {
    awk -v section="$2" -v key="$3" '
      /^[ \t]*[;#]/ {next}
      /^[ \t]*\[/ {s=$0; sub(/^[ \t]*\[/,"",s); sub(/\].*$/,"",s); next}
      s==section {p=index($0,"="); if(!p) next; k=substr($0,1,p-1); gsub(/^[ \t]+|[ \t]+$/,"",k);
        if(k==key) {v=substr($0,p+1); sub(/[ \t]+[;#].*$/,"",v); gsub(/^[ \t]+|[ \t\r]+$/,"",v); value=v}}
      END {print value}' "$1"
}
printf '=== VPN check: host=%s UTC=%s ===\n' "$(hostname)" "$(date -u +%FT%TZ)"
printf 'Node config: %s\nPlugin config: %s\n' "$NODE_CFG" "$PLUGIN_CFG"
if [[ $EUID -ne 0 ]]; then printf 'ERROR: run with sudo for firewall diagnostics\n' >&2; exit 2; fi
for cmd in ip ss sysctl iptables awk; do
    command -v "$cmd" >/dev/null || { printf 'ERROR: missing command %s\n' "$cmd" >&2; exit 2; }
done
ip -brief -4 address show
WAN_IF="${WAN_IF:-$(ip -4 route show default | awk 'NR==1 {for(i=1;i<=NF;i++) if($i=="dev") print $(i+1)}')}"
printf 'Server label: %s | WAN=%s | TUN=%s | subnet=%s\n' "${SERVER_LABEL:-$(hostname)}" "$WAN_IF" "$TUN_IF" "$VPN_SUBNET"
[[ -n "$WAN_IF" ]] || { fail 'No default IPv4 route; set WAN_IF explicitly'; exit 1; }
[[ $(sysctl -n net.ipv4.ip_forward) == 1 ]] && ok 'IPv4 forwarding' || fail 'IPv4 forwarding disabled'
iptables -t nat -C POSTROUTING -s "$VPN_SUBNET" -o "$WAN_IF" -j MASQUERADE && ok 'NAT rule present' || fail 'NAT rule missing (command error above)'
iptables -C FORWARD -i "$TUN_IF" -s "$VPN_SUBNET" -o "$WAN_IF" -j ACCEPT && ok 'VPN outbound rule' || fail 'VPN outbound rule missing'
iptables -C FORWARD -i "$WAN_IF" -o "$TUN_IF" -d "$VPN_SUBNET" -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT && ok 'VPN return rule' || fail 'VPN return rule missing'
warn 'Rule presence does not prove reachability: earlier DROP rules/cloud firewall may override it.'
if ip -4 addr show dev "$TUN_IF"; then
    ip -4 -o addr show dev "$TUN_IF" | awk -v gw="$VPN_GW" '{split($4,a,"/"); if(a[1]==gw) found=1} END {exit !found}' && ok 'VPN gateway address' || fail "Expected gateway $VPN_GW missing"
else fail "TUN $TUN_IF absent; inspect plugin initialization"; fi
if [[ -f "$PLUGIN_CFG" ]]; then
    [[ $(cfg "$PLUGIN_CFG" srv_vpn enabled) == true ]] && ok 'Plugin enabled' || fail 'Plugin enabled is not true'
    [[ $(cfg "$PLUGIN_CFG" srv_vpn allow_free_srv) == true ]] && ok 'Free service enabled in plugin config' || fail 'Plugin allow_free_srv is not true'
else fail "Missing plugin config: $PLUGIN_CFG"; fi
if [[ -f "$NODE_CFG" ]]; then
    net=$(cfg "$NODE_CFG" srv_vpn net)
    [[ -n "$net" ]] && ok "SDK network name: $net (Offline is allowed for free mode)" || fail 'SDK [srv_vpn] net missing; current SDK still uses node global config'
    transports=$(cfg "$NODE_CFG" server transports)
    transports=${transports:-'[http,udp,tls,websocket,dns]'}
    transports=${transports//[\[\],]/ }
    for transport in $transports; do
        case "$transport" in http) port=8079; protocol=tcp;; udp) port=8081; protocol=udp;; tls) port=8082; protocol=tcp;; websocket) port=8083; protocol=tcp;; dns) port=8084; protocol=udp;; *) fail "Unknown transport: $transport"; continue;; esac
        configured=$(cfg "$NODE_CFG" "server_transport_$transport" port)
        port=${configured:-$port}
        printf '\nListener %s/%s port %s:\n' "$transport" "$protocol" "$port"
        if [[ "$protocol" == tcp ]]; then sockets=$(ss -H -lntp "sport = :$port"); else sockets=$(ss -H -lnup "sport = :$port"); fi
        [[ -n "$sockets" ]] && { printf '%s\n' "$sockets"; ok "$transport listener"; } || fail "$transport listener absent"
    done
    warn 'Config parsing covers these files only; inspect cfg.d overrides and actual listener output.'
else fail "Missing node config: $NODE_CFG"; fi
case "$DNS_MODE" in
    plugin) printf 'DNS mode: plugin forwarding; dnsmasq is not required.\n';;
    dnsmasq)
        systemctl is-active dnsmasq || fail 'dnsmasq inactive'
        if command -v dig >/dev/null; then
            answer=$(dig +short +time=2 +tries=1 @"$VPN_GW" example.com A) && [[ -n "$answer" ]] && ok "DNS reply: $answer" || fail 'No DNS reply from VPN gateway'
        else fail 'Install dig to test DNS'; fi;;
    external) warn 'External DNS must be tested from a VPN client';;
    *) fail "Unknown DNS_MODE: $DNS_MODE";;
esac
printf '\nRecent node errors (historical entries may belong to a prior start):\n'
if command -v journalctl >/dev/null; then journalctl -u cellframe-node.service -p warning -n 30 --no-pager; fi
warn 'A listening transport is not proof that VPN service UID 1 is registered. Check plugin loaded successfully and a real free connection.'
printf '\nResult: %s failed checks on %s\n' "$FAILURES" "${SERVER_LABEL:-$(hostname)}"
(( FAILURES == 0 ))
