#!/usr/bin/env bash

source "$(dirname "$0")/ledger_balance_config.sh"

install_dependencies() {
    local DEPENDENCIES_LIST=("wget")

    echo "─────────────────────"
    echo -ne "${ORANGE}+ Updating package list (apt update)...${RESET}"
    if ! apt update > /dev/null 2>&1; then
        echo -e "${CLEAR_LINE}${FAILED}${RED} Error: failed to update package list (apt update).${RESET}"
        echo "─────────────────────"
        return 1
    fi
    echo -e "${CLEAR_LINE}${CHECKED} Package list successfully updated (apt update)."
    
    for DEP in "${DEPENDENCIES_LIST[@]}"; do
        echo -ne "${ORANGE}+ Checking for required dependency '${DEP}'...${RESET}"
        if ! command -v "$DEP" &> /dev/null; then
            echo -ne "${CLEAR_LINE}${ORANGE}+ Installing required dependency '${DEP}'...${RESET}"
            if ! apt install -y "$DEP" > /dev/null 2>&1; then
                echo -e "${CLEAR_LINE}${FAILED}${RED} Error: failed to install required dependency '${DEP}'.${RESET}"
                echo "─────────────────────"
                return 1
            fi
            echo -e "${CLEAR_LINE}${CHECKED} Dependency '${DEP}' successfully installed."
        else
            echo -e "${CLEAR_LINE}${CHECKED} Dependency '${DEP}' is already installed."
        fi
    done
    return 0
}

install_node_package() {
    local DEB_FILE_URL="$1"
    local DEB_FILE_TAG="$2"
    DEB_FILE_NAME=""
    local DEB_TEMP_PATH=""

    rm -f /tmp/cellframe-node*.deb 2>/dev/null
    echo "─────────────────────"
    echo -ne "${ORANGE}+ ${DEB_FILE_TAG} Downloading node package from public repository...${RESET}"
    if ! wget -q --content-disposition -P /tmp "$DEB_FILE_URL" > /dev/null 2>&1; then
        echo -e "${CLEAR_LINE}${FAILED}${RED} ${DEB_FILE_TAG} Error: failed to download package from ${DEB_FILE_URL}.${RESET}"
        echo "─────────────────────"
        return 1
    fi

    DEB_TEMP_PATH=$(ls -t /tmp/cellframe-node*.deb 2>/dev/null | head -n 1)
    if [[ -z "$DEB_TEMP_PATH" ]]; then
        echo -e "${CLEAR_LINE}${FAILED}${RED} ${DEB_FILE_TAG} Error: downloaded '.deb' file not found.${RESET}"
        echo "─────────────────────"
        return 1
    fi
    DEB_FILE_NAME=$(basename "$DEB_TEMP_PATH")
    echo -e "${CLEAR_LINE}${CHECKED} ${DEB_FILE_TAG} Node package '${DEB_FILE_NAME}' successfully downloaded."

    echo -ne "${ORANGE}+ ${DEB_FILE_TAG} Installing downloaded node package '${DEB_FILE_NAME}'...${RESET}"
    dpkg -i "$DEB_TEMP_PATH" > /dev/null 2>&1
    apt install -f -y > /dev/null 2>&1

    if ! dpkg -l | grep -q "cellframe-node"; then
        echo -e "${CLEAR_LINE}${FAILED}${RED} ${DEB_FILE_TAG} Error: failed to install node package '${DEB_FILE_NAME}'.${RESET}"
        echo "─────────────────────"
        rm -f "$DEB_TEMP_PATH"
        return 1
    fi
    echo -e "${CLEAR_LINE}${CHECKED} ${DEB_FILE_TAG} Node package '${DEB_FILE_NAME}' successfully installed."

    rm -f "$DEB_TEMP_PATH"
    return 0
}


preload_chains_backup() {
    local NODE_TAG="$1"
    local CHAINS_BACKUP_TARGET_PATH="/opt/cellframe-node/var/lib"

    if [[ ! -d "$CHAINS_BACKUP_DIR_PATH" ]]; then
        echo -e "${FAILED}${RED} ${NODE_TAG} Error: chains backup directory '$CHAINS_BACKUP_DIR_PATH' not found.${RESET}"
        echo "─────────────────────"
        return 1
    fi

    echo -ne "${ORANGE}+ ${NODE_TAG} Copying mainnets chains backup to '$CHAINS_BACKUP_TARGET_PATH'...${RESET}"

    if ! cp -r "$CHAINS_BACKUP_DIR_PATH" "$CHAINS_BACKUP_TARGET_PATH"/ 2>/dev/null; then
        echo -e "${CLEAR_LINE}${FAILED}${RED} ${NODE_TAG} Error: failed to copy chains backup to '$CHAINS_BACKUP_TARGET_PATH'.${RESET}"
        echo "─────────────────────"
        return 1
    fi

    echo -e "${CLEAR_LINE}${CHECKED} ${NODE_TAG} Chains backup successfully loaded to '$CHAINS_BACKUP_TARGET_PATH'."
    return 0
}

init_run_node() {
    local OUTPUT_LOG_PATH="$1"
    local NODE_TAG="$2"

    echo "─────────────────────"
    echo -ne "${ORANGE}+ ${NODE_TAG} Configuring node settings before startup...${RESET}"

    if [[ ! -f "$ORIGINAL_CONFIG_PATH" ]]; then
        echo -e "${CLEAR_LINE}${FAILED}${RED} ${NODE_TAG} Error: configuration file '$ORIGINAL_CONFIG_PATH' not found.${RESET}"
        echo "─────────────────────"
        return 1
    fi

    sed -i 's/^debug_mode=false/debug_mode=true/' "$ORIGINAL_CONFIG_PATH"
    sed -i 's/^auto_online=true/auto_online=false/' "$ORIGINAL_CONFIG_PATH"
    sed -i '/^\[ledger\]/,/^\[/{s/^# debug_more=true/debug_more=true/}' "$ORIGINAL_CONFIG_PATH"

    echo -e "${CLEAR_LINE}${CHECKED} ${NODE_TAG} Node pre-launch configuration completed successfully."

    echo -ne "${ORANGE}+ ${NODE_TAG} Starting-up node binary file...${RESET}"

    if [[ ! -f "$ORIGINAL_BINARY_PATH" ]]; then
        echo -e "${CLEAR_LINE}${FAILED}${RED} ${NODE_TAG} Error: node binary file '$ORIGINAL_BINARY_PATH' not found.${RESET}"
        echo "─────────────────────"
        return 1
    fi

    "$ORIGINAL_BINARY_PATH" > /dev/null 2>&1 &
    local NODE_PROCESS_PID=$!
    disown $NODE_PROCESS_PID

    local WAITING_LOG_APPEARANCE=0
    while [[ ! -f "$ORIGINAL_SYNC_LOG_PATH" && $WAITING_LOG_APPEARANCE -lt 5 ]]; do
        sleep 1
        ((WAITING_LOG_APPEARANCE++))
    done

    if [[ ! -f "$ORIGINAL_SYNC_LOG_PATH" ]]; then
        echo -e "${CLEAR_LINE}${FAILED}${RED} ${NODE_TAG} Error: node log file '$ORIGINAL_SYNC_LOG_PATH' was not created after startup.${RESET}"
        echo "─────────────────────"
        return 1
    fi

    echo -e "${CLEAR_LINE}${CHECKED} ${NODE_TAG} Node binary file successfully started (PID: $NODE_PROCESS_PID)."

    if ! extract_sync_log_records "$OUTPUT_LOG_PATH" "$NODE_TAG"; then
        return 1
    fi

    return 0
}

net_sync_percent_obtaining() {
    local NET_NAME="$1"
    local NET_SYNC_STATUS
    NET_SYNC_STATUS=$(cellframe-node-cli net -net "$NET_NAME" get status 2>/dev/null)
    
    local NETS_CURRENT_STATE=$(echo "$NET_SYNC_STATUS" | awk '/states:/{found=1} found && /current:/{print $2; exit}')
    
    if [[ "$NETS_CURRENT_STATE" == "NET_STATE_OFFLINE" ]]; then
        echo "100"
        return
    fi
    
    local ZEROCHAIN_SYNC_PERCENT=$(echo "$NET_SYNC_STATUS" | awk '/zerochain:/{found=1} found && /percent:/{gsub(/[^0-9.]/, "", $2); print $2; exit}')
    local MAINCHAIN_SYNC_PERCENT=$(echo "$NET_SYNC_STATUS" | awk '/main:/{found=1} found && /percent:/{gsub(/[^0-9.]/, "", $2); print $2; exit}')
    
    ZEROCHAIN_SYNC_PERCENT=${ZEROCHAIN_SYNC_PERCENT:-0}
    MAINCHAIN_SYNC_PERCENT=${MAINCHAIN_SYNC_PERCENT:-0}
    
    awk "BEGIN {printf \"%.0f\", ($ZEROCHAIN_SYNC_PERCENT + $MAINCHAIN_SYNC_PERCENT) / 2}"
}

verify_net_sync_completed() {
    local NET_NAME="$1"
    local NET_STATUS
    NET_STATUS=$(cellframe-node-cli net -net "$NET_NAME" get status 2>/dev/null)

    local NETS_CURRENT_STATE=$(echo "$NET_STATUS" | awk '/states:/{found=1} found && /current:/{print $2; exit}')

    if [[ "$NETS_CURRENT_STATE" == "NET_STATE_OFFLINE" ]]; then
        return 0
    fi
    return 1
}

extract_sync_log_records() {
    local OUTPUT_LOG_PATH="$1"
    local OUTPUT_LOG_TAG="$2"
    local OUTPUT_LOG_NAME=$(basename "$OUTPUT_LOG_PATH")
    local TIMEOUT=${SYNC_TIMEOUT:-14400}
    local ELAPSED=0
    local DOTS_COUNT=0

    echo "─────────────────────"
    if [[ ! -f "$ORIGINAL_SYNC_LOG_PATH" ]]; then
        echo -e "${FAILED}${RED} ${OUTPUT_LOG_TAG} Error: log file '$ORIGINAL_SYNC_LOG_PATH' not found.${RESET}"
        echo "─────────────────────"
        return 1
    fi

    local KELVPN_CHAINS_SYNCED=false
    local BACKBONE_CHAINS_SYNCED=false

    local BACKBONE_SYNC_PERCENT="0"
    local KELVPN_SYNC_PERCENT="0"
    local SYNC_PERCENT_UPDATE_COUNTER=0

    while [[ "$KELVPN_CHAINS_SYNCED" == false || "$BACKBONE_CHAINS_SYNCED" == false ]]; do
        if [[ $ELAPSED -ge $TIMEOUT ]]; then
            echo -e "${CLEAR_LINE}${FAILED}${RED} ${OUTPUT_LOG_TAG} Error: network syncing was not completed within ${TIMEOUT}s.${RESET}"
            echo "─────────────────────"
            return 1
        fi

        if verify_net_sync_completed "KelVPN"; then
            KELVPN_CHAINS_SYNCED=true
        fi
        if verify_net_sync_completed "Backbone"; then
            BACKBONE_CHAINS_SYNCED=true
        fi

        if [[ $SYNC_PERCENT_UPDATE_COUNTER -eq 0 ]]; then
            BACKBONE_SYNC_PERCENT=$(net_sync_percent_obtaining "Backbone")
            KELVPN_SYNC_PERCENT=$(net_sync_percent_obtaining "KelVPN")
        fi
        SYNC_PERCENT_UPDATE_COUNTER=$(( (SYNC_PERCENT_UPDATE_COUNTER + 1) % 5 ))

        case $DOTS_COUNT in
            0) echo -ne "${CLEAR_LINE}${ORANGE}⠋ ${OUTPUT_LOG_TAG} Waiting for 'Backbone' [${BACKBONE_SYNC_PERCENT}%] & 'KelVPN' [${KELVPN_SYNC_PERCENT}%] networks syncing   ${RESET}" ;;
            1) echo -ne "${CLEAR_LINE}${ORANGE}⠙ ${OUTPUT_LOG_TAG} Waiting for 'Backbone' [${BACKBONE_SYNC_PERCENT}%] & 'KelVPN' [${KELVPN_SYNC_PERCENT}%] networks syncing.  ${RESET}" ;;
            2) echo -ne "${CLEAR_LINE}${ORANGE}⠴ ${OUTPUT_LOG_TAG} Waiting for 'Backbone' [${BACKBONE_SYNC_PERCENT}%] & 'KelVPN' [${KELVPN_SYNC_PERCENT}%] networks syncing.. ${RESET}" ;;
            3) echo -ne "${CLEAR_LINE}${ORANGE}⠦ ${OUTPUT_LOG_TAG} Waiting for 'Backbone' [${BACKBONE_SYNC_PERCENT}%] & 'KelVPN' [${KELVPN_SYNC_PERCENT}%] networks syncing...${RESET}" ;;
        esac
        DOTS_COUNT=$(( (DOTS_COUNT + 1) % 4 ))
        sleep 1
        ((ELAPSED++))
    done

    local LOG_UPPER_BOUND=1
    local LOG_LOWER_BOUND=$(wc -l < "$ORIGINAL_SYNC_LOG_PATH")

    sed -n "${LOG_UPPER_BOUND},${LOG_LOWER_BOUND}p" "$ORIGINAL_SYNC_LOG_PATH" > "$OUTPUT_LOG_PATH"
    echo -e "${CLEAR_LINE}${CHECKED} ${OUTPUT_LOG_TAG} Syncing completed. Log records saved to '$OUTPUT_LOG_NAME' (lines $LOG_UPPER_BOUND-$LOG_LOWER_BOUND)."
    return 0
}

uninstall_node_package() {
    local NODE_TAG="$1"

    echo -ne "${ORANGE}+ ${NODE_TAG} Uninstalling node package '${DEB_FILE_NAME}' and cleaning up...${RESET}"
    pkill -9 -f "cellframe-node" 2>/dev/null
    sleep 1

    if ! apt purge -y cellframe-node > /dev/null 2>&1; then
        echo -e "${CLEAR_LINE}${FAILED}${RED} ${NODE_TAG} Error: failed to uninstall node package '${DEB_FILE_NAME}'.${RESET}"
        echo "─────────────────────"
        return 1
    fi

    rm -rf /opt/cellframe-node

    echo -e "${CLEAR_LINE}${CHECKED} ${NODE_TAG} Node package '${DEB_FILE_NAME}' successfully uninstalled."
    return 0
}

extract_node_version() {
    local DEB_FILE_URL="$1"
    local DEB_FILE_NAME
    DEB_FILE_NAME=$(basename "$DEB_FILE_URL")
    local NODE_BUILD_VERSION
    NODE_BUILD_VERSION=$(echo "$DEB_FILE_NAME" | grep -oP 'cellframe-node-\K[0-9]+\.[0-9]+-[0-9]+')
    echo "${NODE_BUILD_VERSION:-unknown}"
}

noise_filtration() {
    if [[ ${#LOG_NOISE_PATTERNS[@]} -eq 0 ]]; then
        cat
        return
    fi
    local PATTERN
    PATTERN=$(IFS='|'; echo "${LOG_NOISE_PATTERNS[*]}")
    grep -vE "$PATTERN"
}

compare_sync_log_records() {
    echo "─────────────────────"
    if [[ ! -f "$MASTER_SYNC_LOG_PATH" ]]; then
        echo -e "${FAILED}${RED} Error: log file '$MASTER_SYNC_LOG_PATH' not found.${RESET}"
        echo "─────────────────────"
        return 1
    fi

    if [[ ! -f "$BUILD_SYNC_LOG_PATH" ]]; then
        echo -e "${FAILED}${RED} Error: log file '$BUILD_SYNC_LOG_PATH' not found.${RESET}"
        echo "─────────────────────"
        return 1
    fi

    local MASTER_FILTERED_LOG=$(mktemp)
    local BUILD_FILTERED_LOG=$(mktemp)

    grep -oP '\[(dap_ledger[a-z_]*|dap_chain_net_decree)\] \K.*' "$MASTER_SYNC_LOG_PATH" 2>/dev/null \
        | grep -v '^[[:space:]]' | noise_filtration | sort > "$MASTER_FILTERED_LOG"
    grep -oP '\[(dap_ledger[a-z_]*|dap_chain_net_decree)\] \K.*' "$BUILD_SYNC_LOG_PATH" 2>/dev/null \
        | grep -v '^[[:space:]]' | noise_filtration | sort > "$BUILD_FILTERED_LOG"

    local MASTER_FILTERED_LOG_MD5=$(md5sum "$MASTER_FILTERED_LOG" | awk '{print $1}')
    local BUILD_FILTERED_LOG_MD5=$(md5sum "$BUILD_FILTERED_LOG" | awk '{print $1}')

    if [[ "$MASTER_FILTERED_LOG_MD5" == "$BUILD_FILTERED_LOG_MD5" ]]; then
        echo -e "${CHECKED} No discrepancies found. All records in '$BUILD_SYNC_LOG_NAME' match '$MASTER_SYNC_LOG_NAME'."
        echo "─────────────────────"
        rm -f "$MASTER_FILTERED_LOG" "$BUILD_FILTERED_LOG"
        return 0
    fi

    echo -e "${FAILED}${RED} Discrepancies found in log file records. Sync records comparison:${RESET}"
    echo "─────────────────────"

    local MASTER_VERSION
    MASTER_VERSION=$(extract_node_version "$MASTER_DEB_FILE_NAME")
    local BUILD_VERSION
    BUILD_VERSION=$(extract_node_version "$BUILD_DEB_FILE_NAME")

    local DISCREPANCIES_FILE_LINES=()
    while IFS= read -r header_line; do
        DISCREPANCIES_FILE_LINES+=("$header_line")
    done < <(generate_discrepancies_report_header "$BUILD_SYNC_LOG_NAME" "$BUILD_VERSION" "$MASTER_SYNC_LOG_NAME" "$MASTER_VERSION")

    local FIRST_BLOCK=true
    while IFS= read -r line; do
        if [[ "$line" =~ ^[0-9]+(,[0-9]+)?[acd][0-9]+(,[0-9]+)?$ ]]; then
            if [[ "$FIRST_BLOCK" == false ]]; then
                echo "─────────────────────"
                DISCREPANCIES_FILE_LINES+=("─────────────────────")
            fi
            FIRST_BLOCK=false
        elif [[ "$line" =~ ^---$ ]]; then
            continue
        elif [[ "$line" =~ ^\< ]]; then
            local content="${line#< }"
            content="${content#"${content%%[! ]*}"}"
            echo -e "[EXPECTED] [MASTER] [${MASTER_VERSION}] | ${content}"
            DISCREPANCIES_FILE_LINES+=("[EXPECTED] [MASTER] [${MASTER_VERSION}] | ${content}")
        elif [[ "$line" =~ ^\> ]]; then
            local content="${line#> }"
            content="${content#"${content%%[! ]*}"}"
            echo -e "[RECEIVED] [BUILD] [${BUILD_VERSION}] | ${content}"
            DISCREPANCIES_FILE_LINES+=("[RECEIVED] [BUILD] [${BUILD_VERSION}] | ${content}")
        fi
    done < <(diff "$MASTER_FILTERED_LOG" "$BUILD_FILTERED_LOG" 2>/dev/null)

    echo "─────────────────────"
    DISCREPANCIES_FILE_LINES+=("─────────────────────")
    rm -f "$MASTER_FILTERED_LOG" "$BUILD_FILTERED_LOG"

    local DISCREPANCIES_DUMP_FILE_NAME="${SCRIPT_DIR}/ledger_balance_discrepancies_$(date +%d%m%y).txt"
    printf '%s\n' "${DISCREPANCIES_FILE_LINES[@]}" > "$DISCREPANCIES_DUMP_FILE_NAME"
    echo -e "${CHECKED} All detected discrepancies have been saved to '$(basename "$DISCREPANCIES_DUMP_FILE_NAME")'."
    echo "─────────────────────"
}

execute_sync_logs_comparison() {
    install_dependencies || exit 1

    install_node_package "$MASTER_DEB_FILE_URL" "[MASTER]" || exit 1
    MASTER_DEB_FILE_NAME="$DEB_FILE_NAME"
    preload_chains_backup "[MASTER]" || exit 1
    init_run_node "$MASTER_SYNC_LOG_PATH" "[MASTER]" || exit 1
    uninstall_node_package "[MASTER]" || exit 1

    install_node_package "$BUILD_DEB_FILE_URL" "[BUILD]" || exit 1
    BUILD_DEB_FILE_NAME="$DEB_FILE_NAME"
    preload_chains_backup "[BUILD]" || exit 1
    init_run_node "$BUILD_SYNC_LOG_PATH" "[BUILD]" || exit 1
    uninstall_node_package "[BUILD]" || exit 1

    compare_sync_log_records
}

execute_sync_logs_comparison
