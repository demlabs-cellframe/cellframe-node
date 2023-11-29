#!/bin/bash
# Global settings
export DAP_PREFIX=/Users/$USER/Applications/Cellframe.app/Contents/Resources
export DAP_PREFIX_TPL="\\/Users\\/$USER\\/Applications\\/Cellframe.app\\/Contents\\/Resources"
export DAP_APP_NAME=cellframe-node
export DAP_CHAINS_NAME=core-t
export DAP_CFG_TPL=/Applications/Cellframe.app/Contents/Resources/share/configs/$DAP_APP_NAME.cfg.tpl

#export DAP_INST_DIR=/Applications/Cellframe-Dashboard.app/
export DAP_INST_DIR=$1
# Values
export DAP_DEBUG_MODE=false
export DAP_AUTO_ONLINE=true
export DAP_SERVER_ENABLED=false
export DAP_SERVER_ADDRESS=0.0.0.0
export DAP_SERVER_PORT=8089
export NOTIFY_SRV_ADDR=127.0.0.1
export NOTIFY_SRV_PORT=8080

# Raiden testnet
export DAP_RAIDEN_ENABLED=true
export DAP_RAIDEN_ROLE=full

# Raiden testnet
export DAP_RIEMANN_ENABLED=true
export DAP_RIEMANN_ROLE=full


# Subzero testnet
export DAP_SUBZERO_ENABLED=true
export DAP_SUBZERO_ROLE=full

# Backbone
export DAP_BACKBONE_ENABLED=true
export DAP_BACKBONE_ROLE=full

# Kelvpn
export DAP_KELVPN_ENABLED=true
export DAP_KELVPN_ROLE=full


# Kelvpn-minkowski testnet
export DAP_KELVPN_MINKOWSKI_ENABLED=false
export DAP_KELVPN_MINKOWSKI_ROLE=full

# Milena testnet
export DAP_MILEENA_ENABLED=false
export DAP_MILEENA_ROLE=full

export DAP_DB_DRIVER=sqlite

echo "Init configs with prefix " $DAP_PREFIX
echo $(pwd)
echo $(env)

${DAP_INST_DIR}/Contents/Resources/create_configs_from_tpl.sh

DAP_CFG="$DAP_PREFIX/etc/$DAP_APP_NAME.cfg"
sed -i .old "s/driver=mdbx/driver=${DAP_DB_DRIVER}/g" $DAP_CFG  || true