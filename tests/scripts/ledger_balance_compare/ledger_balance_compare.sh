#!/usr/bin/env bash

source "$(dirname "$0")/ledger_balance_config.sh"

install_dependencies() {
    local DEPENDENCIES_LIST=("wget")
    local LINES_TO_CLEAR=$((3 + 1 + ${#DEPENDENCIES_LIST[@]}))

    echo "─────────────────────"
    echo -e "${ORANGE}+ Updating package list and installing required dependencies...${RESET}"
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

    printf "\033[${LINES_TO_CLEAR}A\033[J"
    echo "─────────────────────"
    echo -e "${CHECKED} Package list updated and required dependencies installed."
    return 0
}

install_node_package() {
    local DEB_FILE_URL="$1"
    local DEB_FILE_TAG="$2"
    local DEB_FILE_NAME=""
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

    echo -ne "${ORANGE}+ ${DEB_FILE_TAG} Installing downloaded node package: '${DEB_FILE_NAME}'...${RESET}"
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
    sed -i 's/^auto_online=false/auto_online=true/' "$ORIGINAL_CONFIG_PATH"
    sed -i '/^\[ledger\]/,/^\[/{s/^# debug_more=true/debug_more=true/}' "$ORIGINAL_CONFIG_PATH"

    echo -e "${CLEAR_LINE}${CHECKED} ${NODE_TAG} Node configuration completed successfully."

    echo -ne "${ORANGE}+ ${NODE_TAG} Starting node binary file...${RESET}"

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

    echo -e "${CLEAR_LINE}${CHECKED} ${NODE_TAG} Node binary successfully started (PID: $NODE_PROCESS_PID)."

    if ! extract_sync_log_records "$OUTPUT_LOG_PATH" "$NODE_TAG"; then
        kill -9 $NODE_PROCESS_PID 2>/dev/null
        return 1
    fi

    echo -ne "${ORANGE}+ ${NODE_TAG} Stopping node process and cleaning up temporary files...${RESET}"
    kill -9 $NODE_PROCESS_PID 2>/dev/null
    sleep 1

    rm -f "$ORIGINAL_SYNC_LOG_PATH"
    rm -f "$ORIGINAL_CONFIG_PATH"

    echo -e "${CLEAR_LINE}${CHECKED} ${NODE_TAG} Node process stopped, temporary files removed."
    return 0
}

extract_sync_log_records() {
    local OUTPUT_LOG_PATH="$1"
    local OUTPUT_LOG_TAG="$2"
    local OUTPUT_LOG_NAME=$(basename "$OUTPUT_LOG_PATH")
    local TIMEOUT=${SYNC_TIMEOUT:-10800}
    local ELAPSED=0
    local DOTS_COUNT=0

    echo "─────────────────────"
    if [[ ! -f "$ORIGINAL_SYNC_LOG_PATH" ]]; then
        echo -e "${FAILED}${RED} ${OUTPUT_LOG_TAG} Error: log file '$ORIGINAL_SYNC_LOG_PATH' not found.${RESET}"
        echo "─────────────────────"
        return 1
    fi

    while ! grep -q '\*\*\* DEBUG MODE \*\*\*' "$ORIGINAL_SYNC_LOG_PATH" 2>/dev/null; do
        if [[ $ELAPSED -ge $TIMEOUT ]]; then
            echo -e "${FAILED}${RED} ${OUTPUT_LOG_TAG} Error: network syncing did not start within ${TIMEOUT}s.${RESET}"
            echo "─────────────────────"
            return 1
        fi
        sleep 1
        ((ELAPSED++))
    done

    ELAPSED=0

    local KELVPN_CHAINS_SYNCED=false
    local BACKBONE_CHAINS_SYNCED=false

    while [[ "$KELVPN_CHAINS_SYNCED" == false || "$BACKBONE_CHAINS_SYNCED" == false ]]; do
        if [[ $ELAPSED -ge $TIMEOUT ]]; then
            echo -e "${CLEAR_LINE}${FAILED}${RED} ${OUTPUT_LOG_TAG} Error: network syncing was not completed within ${TIMEOUT}s.${RESET}"
            echo "─────────────────────"
            return 1
        fi

        if grep -q 'All chains in net KelVPN synced, no need new sync request' "$ORIGINAL_SYNC_LOG_PATH" 2>/dev/null; then
            KELVPN_CHAINS_SYNCED=true
        fi
        if grep -q 'All chains in net Backbone synced, no need new sync request' "$ORIGINAL_SYNC_LOG_PATH" 2>/dev/null; then
            BACKBONE_CHAINS_SYNCED=true
        fi

        case $DOTS_COUNT in
            0) echo -ne "${CLEAR_LINE}${ORANGE}⠋ ${OUTPUT_LOG_TAG} Waiting for 'Backbone' & 'KelVPN' networks syncing   ${RESET}" ;;
            1) echo -ne "${CLEAR_LINE}${ORANGE}⠙ ${OUTPUT_LOG_TAG} Waiting for 'Backbone' & 'KelVPN' networks syncing.  ${RESET}" ;;
            2) echo -ne "${CLEAR_LINE}${ORANGE}⠴ ${OUTPUT_LOG_TAG} Waiting for 'Backbone' & 'KelVPN' networks syncing.. ${RESET}" ;;
            3) echo -ne "${CLEAR_LINE}${ORANGE}⠦ ${OUTPUT_LOG_TAG} Waiting for 'Backbone' & 'KelVPN' networks syncing...${RESET}" ;;
        esac
        DOTS_COUNT=$(( (DOTS_COUNT + 1) % 4 ))
        sleep 1
        ((ELAPSED++))
    done

    local LOG_UPPER_BOUND=$(grep -n '\*\*\* DEBUG MODE \*\*\*' "$ORIGINAL_SYNC_LOG_PATH" | tail -n 1 | cut -d: -f1)
    local KELVPN_SYNC_TRACKER=$(grep -n 'All chains in net KelVPN synced, no need new sync request' "$ORIGINAL_SYNC_LOG_PATH" | tail -n 1 | cut -d: -f1)
    local BACKBONE_SYNC_TRACKER=$(grep -n 'All chains in net Backbone synced, no need new sync request' "$ORIGINAL_SYNC_LOG_PATH" | tail -n 1 | cut -d: -f1)
    local LOG_LOWER_BOUND=$((KELVPN_SYNC_TRACKER > BACKBONE_SYNC_TRACKER ? KELVPN_SYNC_TRACKER : BACKBONE_SYNC_TRACKER))

    sed -n "${LOG_UPPER_BOUND},${LOG_LOWER_BOUND}p" "$ORIGINAL_SYNC_LOG_PATH" > "$OUTPUT_LOG_PATH"
    echo -e "${CLEAR_LINE}${CHECKED} ${OUTPUT_LOG_TAG} Syncing completed. Log records saved to '$OUTPUT_LOG_NAME' (lines $LOG_UPPER_BOUND-$LOG_LOWER_BOUND)."
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

    grep -oP '\[(dap_ledger[a-z_]*|dap_chain_net_decree)\] \K.*' "$MASTER_SYNC_LOG_PATH" > "$MASTER_FILTERED_LOG" 2>/dev/null
    grep -oP '\[(dap_ledger[a-z_]*|dap_chain_net_decree)\] \K.*' "$BUILD_SYNC_LOG_PATH" > "$BUILD_FILTERED_LOG" 2>/dev/null

    local LOGS_COMPARE_RESULT=$(diff "$MASTER_FILTERED_LOG" "$BUILD_FILTERED_LOG" 2>/dev/null)

    if [[ -n "$LOGS_COMPARE_RESULT" ]]; then
        echo -e "${FAILED}${RED} Discrepancies found in log file records. Sync records comparison:${RESET}"
        echo "─────────────────────"
        local FIRST_BLOCK=true
        while IFS= read -r line; do
            if [[ "$line" =~ ^[0-9]+(,[0-9]+)?[acd][0-9]+(,[0-9]+)?$ ]]; then
                if [[ "$FIRST_BLOCK" == false ]]; then
                    echo "─────────────────────"
                fi
                FIRST_BLOCK=false
            elif [[ "$line" =~ ^---$ ]]; then
                continue
            elif [[ "$line" =~ ^\< ]]; then
                echo -e "[EXPECTED] [MASTER] | ${line#< }"
            elif [[ "$line" =~ ^\> ]]; then
                echo -e "[RECEIVED] [CBUILD] | ${line#> }"
            fi
        done < <(echo "$LOGS_COMPARE_RESULT")
        echo "─────────────────────"
    else
        echo -e "${CHECKED} No discrepancies found. All records in '$BUILD_SYNC_LOG_NAME' match '$MASTER_SYNC_LOG_NAME'."
        echo "─────────────────────"
    fi
    rm -f "$MASTER_FILTERED_LOG" "$BUILD_FILTERED_LOG"
}

execute_sync_logs_comparison() {
    install_dependencies || exit 1
    install_node_package "$MASTER_DEB_FILE_URL" "[MASTER]" || exit 1
    init_run_node "$MASTER_SYNC_LOG_PATH" "[MASTER]" || exit 1
    install_node_package "$BUILD_DEB_FILE_URL" "[CBUILD]" || exit 1
    init_run_node "$BUILD_SYNC_LOG_PATH" "[CBUILD]" || exit 1
    compare_sync_log_records
}

execute_sync_logs_comparison
