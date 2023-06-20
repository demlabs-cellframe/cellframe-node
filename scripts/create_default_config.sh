#!/bin/bash -e

RED='\033[0;31m'
CLEAR='\033[0m'

DAP_APP_NAME="cellframe-node"
DAP_PREFIX="${INSTALL_ROOT}/opt/$DAP_APP_NAME"
AUTO_ONLINE="true"
SERVER_ENABLED="true"
SERVER_ADDR="0.0.0.0"
SERVER_PORT="8079"
NOTIFY_ADDR="127.0.0.1"
NOTIFY_PORT="8080"
DEBUG_MODE="false"

# 1. Configure networks

NETS=( $(find $DAP_PREFIX/etc/network/* -type d -exec basename {} \; | tr '\n' ' ' | head -c -1) )
NODE_ROLE="full" # Use 'full' role for default configuration

for NET_NAME in "${NETS[@]}"
do
    DAP_CFG_NET="$DAP_PREFIX/etc/network/$NET_NAME.cfg"
    DAP_CFG_NET_TPL="$DAP_PREFIX/share/configs/network/$NET_NAME.cfg.tpl"

    if [[ -f $DAP_CFG_NET ]] ; then # Don't overwrite old configuration file
        echo "-- Old configuration file found for $NET_NAME network, not overwriting..."
        DAP_CFG_NET="$DAP_CFG_NET.new"
    fi

    cat $DAP_CFG_NET_TPL > $DAP_CFG_NET
    echo "-- Creating configuration file $DAP_CFG_NET..."
    sed -i "s|{NODE_TYPE}|$NODE_ROLE|g" $DAP_CFG_NET
done

# 2. Configure cellframe-node

DAP_CFG="$DAP_PREFIX/etc/$DAP_APP_NAME.cfg"
DAP_CFG_TPL="$DAP_PREFIX/share/configs/$DAP_APP_NAME.cfg.tpl"

if [[ -f $DAP_CFG ]] ; then # Don't overwrite old configuration file
    echo "-- Old configuration file found for $DAP_APP_NAME, not overwriting..."
    DAP_CFG="$DAP_CFG.new"
fi

cat $DAP_CFG_TPL > $DAP_CFG
echo "-- Creating configuration file $DAP_CFG..."
sed -i "s|{PREFIX}|$DAP_PREFIX|g" $DAP_CFG
sed -i "s|{DEBUG_MODE}|$DEBUG_MODE|g" $DAP_CFG
sed -i "s|{AUTO_ONLINE}|$AUTO_ONLINE|g" $DAP_CFG
sed -i "s|{SERVER_ENABLED}|$SERVER_ENABLED|g" $DAP_CFG
sed -i "s|{SERVER_PORT}|$SERVER_PORT|g" $DAP_CFG
sed -i "s|{SERVER_ADDR}|$SERVER_ADDR|g" $DAP_CFG
sed -i "s|{NOTIFY_SRV_ADDR}|$NOTIFY_ADDR|g" $DAP_CFG
sed -i "s|{NOTIFY_SRV_PORT}|$NOTIFY_PORT|g" $DAP_CFG

echo "-- Creating directories..."
mkdir -pv $DAP_PREFIX/var/{run,lib/wallet,lib/global_db,lib/plugins,log} # Create the directories

if [[ $(command -v logrotate) && -d /etc/logrotate.d ]] ; then ## Logrotate installed and path is valid?
    echo "-- Symlinking logrotate file..."
    ln -sf $DAP_PREFIX/share/logrotate/$DAP_APP_NAME /etc/logrotate.d/$DAP_APP_NAME # Symlink for logrotate
else
    echo -e "$RED-- Logrotate not available on your system, skipping logrotate configuration file installation...$CLEAR"
fi

if [[ $(ps --no-headers -o comm 1) == "systemd" && -d /etc/systemd/system ]] ; then
    echo "-- Installing systemd unit file..."
    ln -sf $DAP_PREFIX/share/$DAP_APP_NAME.service /etc/systemd/system/$DAP_APP_NAME.service # Symlink for systemd unit file
    systemctl is-active --quiet $DAP_APP_NAME.service && systemctl stop $DAP_APP_NAME.service && echo "-- Stopped $DAP_APP_NAME.service..."
    systemctl daemon-reload # Reload unit files
    echo "-- Starting $DAP_APP_NAME.service..."
    systemctl enable --quiet --now $DAP_PREFIX/share/$DAP_APP_NAME.service # And finally launch the service
else
    echo -e "$RED-- Systemd not available on your system, skipping $DAP_APP_NAME.service installation...$CLEAR"
fi

if [[ -d /etc/profile.d ]] ; then
    echo "-- Adding $DAP_APP_NAME to your \$PATH..."
    ln -sf $DAP_PREFIX/share/profile.d/$DAP_APP_NAME.sh /etc/profile.d/$DAP_APP_NAME.sh
    source /etc/profile.d/$DAP_APP_NAME.sh
fi