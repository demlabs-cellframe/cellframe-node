#!/bin/bash

# CVE ID Generator for Cellframe SDK
# Generates CVE identifiers in the format: CVE-CF-YYYY-CATEGORY-SEQ
# Author: Cellframe SDK Security Team
# Version: 1.0.0

set -e

# Configuration
PROJECT_INITIALS="CF"
SEQUENCE_FILE=".cve_sequence"
LOG_FILE=".cve_log.txt"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print usage
usage() {
    echo "Usage: $0 [category] [description]"
    echo ""
    echo "Categories:"
    echo "  STAKE     - Staking-related vulnerabilities"
    echo "  TX        - Transaction processing vulnerabilities" 
    echo "  CONSENSUS - Consensus mechanism vulnerabilities"
    echo "  CRYPTO    - Cryptographic vulnerabilities"
    echo "  NETWORK   - Network protocol vulnerabilities"
    echo "  MEMORY    - Memory management vulnerabilities"
    echo "  AUTH      - Authentication and authorization vulnerabilities"
    echo ""
    echo "Examples:"
    echo "  $0 STAKE 'Buffer overflow in staking validation'"
    echo "  $0 TX 'Race condition in transaction processing'"
    echo "  $0 CRYPTO 'Weak cryptographic key generation'"
    echo ""
    echo "Generated CVE IDs follow the format: CVE-CF-YYYY-CATEGORY-SEQ"
}

# Function to log CVE creation
log_cve() {
    local cve_id="$1"
    local category="$2"
    local description="$3"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo "$timestamp|$cve_id|$category|$description" >> "$LOG_FILE"
}

# Function to get next sequence number
get_next_sequence() {
    local category="$1"
    local year=$(date +%Y)
    local sequence_key="${year}_${category}"
    
    # Create sequence file if it doesn't exist
    if [[ ! -f "$SEQUENCE_FILE" ]]; then
        touch "$SEQUENCE_FILE"
    fi
    
    # Get current sequence for this category/year
    local current_seq=$(grep "^${sequence_key}:" "$SEQUENCE_FILE" | cut -d: -f2 || echo "0")
    
    # Increment sequence
    local next_seq=$((current_seq + 1))
    
    # Update sequence file
    if grep -q "^${sequence_key}:" "$SEQUENCE_FILE"; then
        sed -i "s/^${sequence_key}:${current_seq}/${sequence_key}:${next_seq}/" "$SEQUENCE_FILE"
    else
        echo "${sequence_key}:${next_seq}" >> "$SEQUENCE_FILE"
    fi
    
    printf "%03d" $next_seq
}

# Function to validate category
validate_category() {
    local category="$1"
    local valid_categories=("STAKE" "TX" "CONSENSUS" "CRYPTO" "NETWORK" "MEMORY" "AUTH")
    
    for valid_cat in "${valid_categories[@]}"; do
        if [[ "$category" == "$valid_cat" ]]; then
            return 0
        fi
    done
    
    echo -e "${RED}Error: Invalid category '$category'${NC}"
    echo ""
    echo "Valid categories:"
    for valid_cat in "${valid_categories[@]}"; do
        echo "  $valid_cat"
    done
    return 1
}

# Main function
main() {
    # Check arguments
    if [[ $# -lt 2 ]]; then
        usage
        exit 1
    fi
    
    local category="$1"
    local description="$2"
    local year=$(date +%Y)
    
    # Validate category
    if ! validate_category "$category"; then
        exit 1
    fi
    
    # Generate CVE ID
    local sequence=$(get_next_sequence "$category")
    local cve_id="CVE-${PROJECT_INITIALS}-${year}-${category}-${sequence}"
    
    # Log the CVE creation
    log_cve "$cve_id" "$category" "$description"
    
    # Output result
    echo ""
    echo -e "${GREEN}✓ CVE ID Generated Successfully!${NC}"
    echo ""
    echo -e "${BLUE}CVE ID:${NC} $cve_id"
    echo -e "${BLUE}Category:${NC} $category"
    echo -e "${BLUE}Year:${NC} $year"
    echo -e "${BLUE}Description:${NC} $description"
    echo ""
    echo -e "${YELLOW}This CVE ID has been logged to $LOG_FILE${NC}"
    echo ""
    
    # Copy to clipboard if xclip is available
    if command -v xclip &> /dev/null; then
        echo -n "$cve_id" | xclip -selection clipboard
        echo -e "${GREEN}✓ CVE ID copied to clipboard!${NC}"
        echo ""
    fi
}

# Run main function
main "$@"
