#!/bin/bash -e
if [ ! -d "$DAP_PREFIX" ]; then
    echo "Need to export proper DAP_PREFIX as prefix path for this scripts"
    exit 2
fi

if [ ! "$DAP_APP_NAME" ]; then
    echo "Need to export DAP_APP_NAME for this scripts"
    exit 3
fi

if [ ! "$DAP_CHAINS_NAME" ]; then
    echo "Need to export DAP_CHAINS_NAME for this scripts"
    exit 4
fi

# set default values
[ "$DAP_DEBUG_MODE_NAME" ] || DAP_DEBUG_MODE="false"
[ "$DAP_AUTO_ONLINE" ] || DAP_AUTO_ONLINE="true"
[ "$DAP_SERVER_ENABLED" ] || DAP_SERVER_ENABLED="false"
[ "$DAP_SERVER_PORT" ] || DAP_SERVER_PORT="8079"
[ "$DAP_SERVER_ADDR" ] || DAP_SERVER_ADDR="0.0.0.0"
[ "$DAP_NOTIFY_SRV_PORT" ] || DAP_SERVER_PORT="8080"
[ "$DAP_NOTIFY_SRV_ADDR" ] || DAP_SERVER_ADDR="127.0.0.1"

DAP_CFG_TPL="$DAP_PREFIX/share/configs/$DAP_APP_NAME.cfg.tpl"



# Init node config
if [ ! -e "$DAP_CFG" ]; then
    DAP_CFG="$DAP_PREFIX/etc/$DAP_APP_NAME.cfg"
fi

if [ -e "$DAP_CFG" ]; then
    DAP_CFG="$DAP_PREFIX/etc/$DAP_APP_NAME.cfg.new"
else
    DAP_CFG="$DAP_PREFIX/etc/$DAP_APP_NAME.cfg"
fi

cat $DAP_CFG_TPL > $DAP_CFG || true
sed -i .old "s/{DEBUG_MODE}/$DAP_DEBUG_MODE/g" $DAP_CFG  || true
sed -i .old "s/{AUTO_ONLINE}/$DAP_AUTO_ONLINE/g" $DAP_CFG  || true
sed -i .old "s/{SERVER_ENABLED}/$DAP_SERVER_ENABLED/g" $DAP_CFG  || true
sed -i .old "s/{SERVER_PORT}/$DAP_SERVER_PORT/g" $DAP_CFG  || true
sed -i .old "s/{SERVER_ADDR}/$DAP_SERVER_ADDR/g" $DAP_CFG  || true
sed -i .old "s/{NOTIFY_SRV_PORT}/$DAP_NOTIFY_SRV_PORT/g" $DAP_CFG  || true
sed -i .old "s/{NOTIFY_SRV_ADDR}/$DAP_NOTIFY_SRV_ADDR/g" $DAP_CFG  || true
sed -i .old "s/{PREFIX}/$DAP_PREFIX_TPL/g" $DAP_CFG  || true
rm $DAP_CFG.old

# Init chains
NET_NAME="core-t"

if [ "$DAP_CORE_T_ENABLED"="true" ]; then
    DAP_CFG_NET="$DAP_PREFIX/etc/network/$NET_NAME.cfg"
    DAP_CFG_NET_TPL="$DAP_PREFIX/share/configs/network/$NET_NAME.cfg.tpl"
    DAP_NET_CFG=""
    if [ -e "$DAP_CFG_NET" ]; then
	DAP_NET_CFG="$DAP_PREFIX/etc/network/$NET_NAME.cfg.new"
    else
	DAP_NET_CFG="$DAP_PREFIX/etc/network/$NET_NAME.cfg"
    fi

    cat $DAP_CFG_NET_TPL > $DAP_NET_CFG || true
    sed -i .old "s/{NODE_TYPE}/$DAP_CORE_T_ROLE/" $DAP_NET_CFG  || true
    rm $DAP_NET_CFG.old
fi

# Init chains
NET_NAME="kelvin-testnet"

if [ "$DAP_KELVIN_TESTNET_ENABLED"="true" ]; then
    DAP_CFG_NET="$DAP_PREFIX/etc/network/$NET_NAME.cfg"
    DAP_CFG_NET_TPL="$DAP_PREFIX/share/configs/network/$NET_NAME.cfg.tpl"
    DAP_NET_CFG=""
    if [ -e "$DAP_CFG_NET" ]; then
	DAP_NET_CFG="$DAP_PREFIX/etc/network/$NET_NAME.cfg.new"
    else
	DAP_NET_CFG="$DAP_PREFIX/etc/network/$NET_NAME.cfg"
    fi

    cat $DAP_CFG_NET_TPL > $DAP_NET_CFG || true
    sed -i .old "s/{NODE_TYPE}/$DAP_KELVIN_TESTNET_ROLE/" $DAP_NET_CFG  || true
    rm $DAP_NET_CFG.old
fi

NET_NAME="subzero"

if [ "$DAP_SUBZERO_ENABLED"="true" ]; then
    DAP_CFG_NET="$DAP_PREFIX/etc/network/$NET_NAME.cfg"
    DAP_CFG_NET_TPL="$DAP_PREFIX/share/configs/network/$NET_NAME.cfg.tpl"
    DAP_NET_CFG=""
    if [ -e "$DAP_CFG_NET" ]; then
	DAP_NET_CFG="$DAP_PREFIX/etc/network/$NET_NAME.cfg.new"
    else
	DAP_NET_CFG="$DAP_PREFIX/etc/network/$NET_NAME.cfg"
    fi

    cat $DAP_CFG_NET_TPL > $DAP_NET_CFG || true
    sed -i .old "s/{NODE_TYPE}/$DAP_SUBZERO_ROLE/" $DAP_NET_CFG  || true
    rm $DAP_NET_CFG.old
fi

NET_NAME="kelvpn-minkowski"

if [ "$DAP_KELVPN_MINKOWSKI_ENABLED"="true" ]; then
    DAP_CFG_NET="$DAP_PREFIX/etc/network/$NET_NAME.cfg"
    DAP_CFG_NET_TPL="$DAP_PREFIX/share/configs/network/$NET_NAME.cfg.tpl"
    DAP_NET_CFG=""
    if [ -e "$DAP_CFG_NET" ]; then
	DAP_NET_CFG="$DAP_PREFIX/etc/network/$NET_NAME.cfg.new"
    else
	DAP_NET_CFG="$DAP_PREFIX/etc/network/$NET_NAME.cfg"
    fi

    cat $DAP_CFG_NET_TPL > $DAP_NET_CFG || true
    sed -i .old "s/{NODE_TYPE}/$DAP_KELVPN_MINKOWSKI_ROLE/" $DAP_NET_CFG  || true
    rm $DAP_NET_CFG.old
fi