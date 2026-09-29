#!/usr/bin/env bash
# ============================================================================
# vpn-server-setup.sh — Настройка ОС для VPN-сервера CellFrame/KelVPN
#
# Запускать от root на сервере (144.202.45.230).
# ============================================================================

# НЕ используем set -e — чтобы не падать на каждой ошибке
set -u

# ─── Конфигурация ──────────────────────────────────────────────────────────
VPN_SUBNET="${VPN_SUBNET:-10.11.12.0/24}"
VPN_GW="${VPN_GW:-10.11.12.1}"
DNS_UPSTREAM="${DNS_UPSTREAM:-8.8.8.8,1.1.1.1}"
NODE_CFG="${NODE_CFG:-/opt/cellframe-node/etc/cellframe-node.cfg}"
NODE_CFG_FALLBACK="/home/kostya/Project_1/cellframe-node/dist/share/configs/cellframe-node.cfg"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info()  { echo -e "${GREEN}[+]${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
error() { echo -e "${RED}[✗]${NC} $*"; }

# Таймаут для команд, которые могут зависнуть
run_with_timeout() {
    local timeout=$1; shift
    timeout "$timeout" "$@" 2>/dev/null
    return $?
}

# ─── Проверка root ─────────────────────────────────────────────────────────
if [[ $EUID -ne 0 ]]; then
    error "Запустите от root: sudo $0"
    exit 1
fi

# ─── Автоопределение WAN ──────────────────────────────────────────────────
WAN_IF=$(ip -4 route show default 2>/dev/null | awk '{print $5; exit}')
WAN_IF="${WAN_IF:-eth0}"
info "WAN: $WAN_IF | VPN: $VPN_SUBNET | GW: $VPN_GW"

# ═══════════════════════════════════════════════════════════════════════════
# 1. IP Forwarding
# ═══════════════════════════════════════════════════════════════════════════
echo ""
info "=== 1. IP Forwarding ==="
if [[ "$(sysctl -n net.ipv4.ip_forward 2>/dev/null)" != "1" ]]; then
    sysctl -w net.ipv4.ip_forward=1
    grep -q '^net.ipv4.ip_forward=1' /etc/sysctl.conf 2>/dev/null || echo 'net.ipv4.ip_forward=1' >> /etc/sysctl.conf
    info "Включён"
else
    info "Уже включён"
fi

# ═══════════════════════════════════════════════════════════════════════════
# 2. iptables
# ═══════════════════════════════════════════════════════════════════════════
echo ""
info "=== 2. iptables NAT ==="

# Удаляем старые (игнорируем ошибки)
iptables -t nat -D POSTROUTING -s "$VPN_SUBNET" -o "$WAN_IF" -j MASQUERADE 2>/dev/null || true
iptables -D FORWARD -i tun+ -o "$WAN_IF" -j ACCEPT 2>/dev/null || true
iptables -D FORWARD -i "$WAN_IF" -o tun+ -m state --state RELATED,ESTABLISHED -j ACCEPT 2>/dev/null || true
iptables -t mangle -D FORWARD -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu 2>/dev/null || true

# Добавляем новые
iptables -t nat -A POSTROUTING -s "$VPN_SUBNET" -o "$WAN_IF" -j MASQUERADE && info "MASQUERADE OK" || error "MASQUERADE FAIL"
iptables -A FORWARD -i tun+ -o "$WAN_IF" -j ACCEPT && info "FORWARD tun+ -> $WAN_IF OK" || error "FORWARD FAIL"
iptables -A FORWARD -i "$WAN_IF" -o tun+ -m state --state RELATED,ESTABLISHED -j ACCEPT && info "FORWARD $WAN_IF -> tun+ OK" || error "FORWARD FAIL"
iptables -t mangle -A FORWARD -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu && info "MSS clamping OK" || error "MSS FAIL"

# Сохраняем
mkdir -p /etc/iptables
iptables-save > /etc/iptables/rules.v4 && info "Сохранено в /etc/iptables/rules.v4" || warn "Не удалось сохранить"

# Systemd-сервис для восстановления (без daemon-reload — он может зависнуть)
if [[ ! -f /etc/systemd/system/vpn-iptables.service ]]; then
    cat > /etc/systemd/system/vpn-iptables.service <<'EOF'
[Unit]
Description=Restore VPN iptables rules
Before=cellframe-node.service
After=network.target

[Service]
Type=oneshot
ExecStart=/sbin/iptables-restore /etc/iptables/rules.v4
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF
    info "Создан vpn-iptables.service (daemon-reload при следующей загрузке)"
fi

# ═══════════════════════════════════════════════════════════════════════════
# 3. DNS (dnsmasq)
# ═══════════════════════════════════════════════════════════════════════════
echo ""
info "=== 3. DNS (dnsmasq) ==="

if ! command -v dnsmasq &>/dev/null; then
    info "Устанавливаю dnsmasq (с таймаутом 120с)..."
    if command -v apt-get &>/dev/null; then
        # Убиваем возможные зависшие apt процессы
        killall -q apt-get apt 2>/dev/null || true
        rm -f /var/lib/dpkg/lock-frontend /var/lib/dpkg/lock /var/cache/apt/archives/lock 2>/dev/null
        DEBIAN_FRONTEND=noninteractive run_with_timeout 120 apt-get install -y -qq dnsmasq
    elif command -v dnf &>/dev/null; then
        run_with_timeout 120 dnf install -y -q dnsmasq
    elif command -v pacman &>/dev/null; then
        run_with_timeout 120 pacman -S --noconfirm dnsmasq
    else
        error "Не удалось установить dnsmasq — установите вручную"
    fi
fi

if command -v dnsmasq &>/dev/null; then
    DNSMASQ_CONF="/etc/dnsmasq.d/vpn.conf"
    IFS=',' read -ra DNS_SERVERS <<< "$DNS_UPSTREAM"

    cat > "$DNSMASQ_CONF" <<EOF
listen-address=${VPN_GW}
bind-interfaces
no-resolv
EOF
    for dns in "${DNS_SERVERS[@]}"; do
        echo "server=${dns}" >> "$DNSMASQ_CONF"
    done
    cat >> "$DNSMASQ_CONF" <<EOF
cache-size=1000
neg-ttl=60
domain-needed
bogus-priv
log-queries
log-facility=/var/log/dnsmasq-vpn.log
EOF
    info "Конфиг: $DNSMASQ_CONF"

    # Проверяем конфликт с systemd-resolved
    if ss -uln 2>/dev/null | grep -q ':53 '; then
        warn "Порт 53 уже занят — возможно systemd-resolved"
        warn "Выполните: systemctl stop systemd-resolved && systemctl disable systemd-resolved"
    fi

    # Перезапуск с таймаутом
    run_with_timeout 10 systemctl restart dnsmasq 2>/dev/null || \
    run_with_timeout 10 service dnsmasq restart 2>/dev/null || \
    warn "Не удалось перезапустить dnsmasq"

    if systemctl is-active --quiet dnsmasq 2>/dev/null; then
        info "dnsmasq запущен на $VPN_GW:53"
    else
        warn "dnsmasq не запущен — проверьте: journalctl -u dnsmasq"
    fi
else
    warn "dnsmasq не установлен — DNS не будет работать"
fi

# ═══════════════════════════════════════════════════════════════════════════
# 4. Конфиг cellframe-node
# ═══════════════════════════════════════════════════════════════════════════
echo ""
info "=== 4. cellframe-node.cfg ==="

CFG_PATH=""
[[ -f "$NODE_CFG" ]] && CFG_PATH="$NODE_CFG"
[[ -z "$CFG_PATH" && -f "$NODE_CFG_FALLBACK" ]] && CFG_PATH="$NODE_CFG_FALLBACK"

if [[ -n "$CFG_PATH" ]]; then
    current_val=$(grep -A5 '^\[srv_vpn\]' "$CFG_PATH" | grep '^enabled=' | head -1 | cut -d= -f2)
    if [[ "$current_val" == "false" ]]; then
        sed -i '/^\[srv_vpn\]/,/^\[/{s/^enabled=false/enabled=true/}' "$CFG_PATH"
        info "[srv_vpn] enabled=false -> true"
    elif [[ "$current_val" == "true" ]]; then
        info "[srv_vpn] уже true"
    else
        warn "Не удалось определить enabled — проверьте вручную: $CFG_PATH"
    fi
else
    warn "Конфиг не найден — включите [srv_vpn] enabled=true вручную"
fi

# ═══════════════════════════════════════════════════════════════════════════
# 5. TUN
# ═══════════════════════════════════════════════════════════════════════════
echo ""
info "=== 5. TUN устройство ==="

if [[ -e /dev/net/tun ]]; then
    info "/dev/net/tun существует"
else
    mkdir -p /dev/net && mknod /dev/net/tun c 10 200 && chmod 666 /dev/net/tun
    info "/dev/net/tun создан"
fi

lsmod 2>/dev/null | grep -q '^tun ' || modprobe tun 2>/dev/null || true

if ip link show tun0 &>/dev/null; then
    tun_addr=$(ip -4 addr show tun0 2>/dev/null | grep -oP 'inet \K[0-9.]+')
    info "tun0: $tun_addr"
    # dnsmasq was started earlier with listen-address=VPN_GW; if tun0 was
    # missing then, it never bound 10.11.12.1 and VPN DNS stays silent
    # (seen in srv-tun.pcap: queries to GW:53, zero replies).
    if command -v dnsmasq &>/dev/null; then
        run_with_timeout 10 systemctl restart dnsmasq 2>/dev/null || \
        run_with_timeout 10 service dnsmasq restart 2>/dev/null || true
        if systemctl is-active --quiet dnsmasq 2>/dev/null; then
            info "dnsmasq перезапущен после появления tun0"
        else
            warn "dnsmasq не активен после рестарта — journalctl -u dnsmasq"
        fi
    fi
else
    warn "tun0 не найден — после старта cellframe-node обязательно:"
    warn "  systemctl restart dnsmasq"
    warn "иначе DNS на ${VPN_GW}:53 не слушает (listen-address до появления tun)"
fi

# ═══════════════════════════════════════════════════════════════════════════
# 6. Порты
# ═══════════════════════════════════════════════════════════════════════════
echo ""
info "=== 6. Порты ==="
for port in 8079 8081; do
    ss -tuln 2>/dev/null | grep -q ":${port} " && info "Порт $port слушает" || warn "Порт $port не слушает"
done

# ═══════════════════════════════════════════════════════════════════════════
# Готово
# ═══════════════════════════════════════════════════════════════════════════
echo ""
info "=========================================="
info "Готово! Далее:"
info "  1. Перезапустите cellframe-node (если tun0 ещё не было)"
info "  2. systemctl restart dnsmasq   # обязательно после появления ${VPN_GW} на tun0"
info "  3. Запустите: ./vpn-server-check.sh"
info "  4. Подключайтесь с клиента (клиентский src должен быть VPN-IP, не LAN)"
info "=========================================="
