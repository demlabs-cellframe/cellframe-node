#!/usr/bin/env bash
# vpn-server-check.sh — Проверка VPN-сервера
set -u

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
ok()   { echo -e "  ${GREEN}PASS${NC}  $*"; }
fail() { echo -e "  ${RED}FAIL${NC}  $*"; }
warn() { echo -e "  ${YELLOW}WARN${NC}  $*"; }

VPN_SUBNET="${VPN_SUBNET:-10.11.12.0/24}"
VPN_GW="${VPN_GW:-10.11.12.1}"
WAN_IF=$(ip -4 route show default 2>/dev/null | awk '{print $5; exit}')
WAN_IF="${WAN_IF:-eth0}"

echo "═══════════════════════════════════════"
echo " VPN Server Check"
echo "═══════════════════════════════════════"

# 1
echo ""
echo "1. IP Forwarding"
[[ "$(sysctl -n net.ipv4.ip_forward 2>/dev/null)" == "1" ]] && ok "ip_forward=1" || fail "ip_forward != 1"

# 2
echo "2. NAT"
iptables -t nat -C POSTROUTING -s "$VPN_SUBNET" -o "$WAN_IF" -j MASQUERADE 2>/dev/null \
    && ok "MASQUERADE $VPN_SUBNET -> $WAN_IF" \
    || fail "MASQUERADE не найден"

# 3
echo "3. FORWARD"
iptables -C FORWARD -i tun+ -o "$WAN_IF" -j ACCEPT 2>/dev/null \
    && ok "tun+ -> $WAN_IF" \
    || fail "Нет FORWARD tun+ -> $WAN_IF"
iptables -C FORWARD -i "$WAN_IF" -o tun+ -m state --state RELATED,ESTABLISHED -j ACCEPT 2>/dev/null \
    && ok "$WAN_IF -> tun+" \
    || fail "Нет FORWARD $WAN_IF -> tun+"

# 4
echo "4. TUN"
if ip link show tun0 &>/dev/null; then
    addr=$(ip -4 addr show tun0 2>/dev/null | grep -oP 'inet \K[0-9.]+')
    [[ "$addr" == "$VPN_GW" ]] && ok "tun0=$addr" || warn "tun0=$addr (ожидается $VPN_GW)"
else
    fail "tun0 не найден"
fi

# 5
echo "5. DNS"
if systemctl is-active --quiet dnsmasq 2>/dev/null; then
    ok "dnsmasq active"
else
    fail "dnsmasq не запущен"
fi
ss -uln 2>/dev/null | grep -q ':53 ' && ok "UDP 53 слушает" || fail "UDP 53 не слушает"

# 6
echo "6. DNS тест"
if command -v dig &>/dev/null; then
    r=$(timeout 3 dig +short +tries=1 @"$VPN_GW" google.com A 2>/dev/null | head -1)
    [[ -n "$r" ]] && ok "dig -> $r" || fail "dig: нет ответа от $VPN_GW"
else
    warn "dig не установлен"
fi

# 7
echo "7. Порты"
for p in 8079 8081; do
    ss -tuln 2>/dev/null | grep -q ":${p} " && ok "Порт $p" || fail "Порт $p"
done

# 8
echo "8. [srv_vpn]"
CFG=""
for f in /opt/cellframe-node/etc/cellframe-node.cfg \
         /home/kostya/Project_1/cellframe-node/dist/share/configs/cellframe-node.cfg; do
    [[ -f "$f" ]] && { CFG="$f"; break; }
done
if [[ -n "$CFG" ]]; then
    v=$(grep -A5 '^\[srv_vpn\]' "$CFG" | grep '^enabled=' | head -1 | cut -d= -f2)
    [[ "$v" == "true" ]] && ok "enabled=true" || fail "enabled=$v"
else
    warn "Конфиг не найден"
fi

echo ""
echo "═══════════════════════════════════════"
