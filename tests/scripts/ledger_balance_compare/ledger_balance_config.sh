#!/usr/bin/env bash

export PATH=/opt/cellframe-node/bin:$PATH

GREEN="\033[0;32m"
RED="\033[0;31m"
ORANGE="\033[38;5;214m"

CLEAR_LINE="\r\033[K"
RESET="\033[0m"

CHECKED="${GREEN}✔${RESET}"
FAILED="${RED}✘${RESET}"

ORIGINAL_CONFIG_PATH="/opt/cellframe-node/etc/cellframe-node.cfg"
ORIGINAL_BINARY_PATH="/opt/cellframe-node/bin/cellframe-node"
ORIGINAL_SYNC_LOG_PATH="/opt/cellframe-node/var/log/cellframe-node.log"

CHAINS_BACKUP_ARCHIVE_NAME="mainnets_chains_backup.tar.gz"
CHAINS_BACKUP_ARCHIVE_PATH="/opt/buildtools/${CHAINS_BACKUP_ARCHIVE_NAME}"
CHAINS_BACKUP_TEMP_PATH="/tmp/mainnets_chains_backup"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

source "${PROJECT_ROOT}/version.mk"
BUILD_PACKAGE_VERSION="${VERSION_MAJOR}.${VERSION_MINOR}-${VERSION_PATCH}"
BUILD_BRANCH="${CI_COMMIT_BRANCH:-master}"

BUILD_DEB_FILE_URL="https://internal-pub.cellframe.net/linux/cellframe-node/${BUILD_BRANCH}/latest-amd64"
BUILD_SYNC_LOG_NAME="cellframe-node-build.log"
BUILD_SYNC_LOG_PATH="${SCRIPT_DIR}/${BUILD_SYNC_LOG_NAME}"

MASTER_DEB_FILE_URL="https://internal-pub.cellframe.net/linux/cellframe-node/master/latest-amd64"
MASTER_SYNC_LOG_NAME="cellframe-node-master.log"
MASTER_SYNC_LOG_PATH="${SCRIPT_DIR}/${MASTER_SYNC_LOG_NAME}"
