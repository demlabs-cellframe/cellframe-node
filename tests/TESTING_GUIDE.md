# Cellframe Node Testing System - Complete Guide for AI Agents

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Test Runner Script (run.sh)](#test-runner-script)
3. [Two Testing Backends](#two-testing-backends)
4. [Network Genesis Process](#network-genesis-process)
5. [Critical Issues and Solutions](#critical-issues-and-solutions)
6. [Configuration Files](#configuration-files)
7. [Certificates and Keys](#certificates-and-keys)
8. [ESBocs Consensus](#esbocs-consensus)
9. [Debugging Commands](#debugging-commands)
10. [Version Differences](#version-differences)

---

## Architecture Overview

### Test System Components

```
tests/
├── run.sh                          # Main test runner (this file orchestrates everything)
├── stage-env/                      # New Python-based testing framework
│   ├── stage-env                   # CLI wrapper script
│   ├── src/                        # Python source code
│   ├── config/templates/          # Jinja2 templates for node configs
│   ├── scenarios/genesis/         # Genesis scenario definitions
│   │   ├── phase1_zerochain.yml   # Phase 1: ROOT nodes + DAG-PoA
│   │   └── phase2_esbocs.yml      # Phase 2: MASTER nodes + ESBocs
│   └── cache/                      # Runtime data (configs, node data)
├── stage-env.cfg                   # Main configuration file
└── ../../tests-in-docker/         # Legacy Docker-based testing (reference implementation)
    └── testnet.sh                  # Working reference implementation
```

### Network Topology

```
Stagenet Test Network:
├── ROOT Nodes (1-3)     # DAG-PoA consensus for zerochain
│   ├── node-1 (root-1)  # 172.20.0.11
│   ├── node-2 (root-2)  # 172.20.0.12
│   └── node-3 (root-3)  # 172.20.0.13
├── MASTER Nodes (4-6)   # ESBocs consensus for mainchain
│   ├── node-4 (master-1) # 172.20.0.14
│   ├── node-5 (master-2) # 172.20.0.15
│   └── node-6 (master-3) # 172.20.0.16
└── FULL Node (7)        # Regular full node
    └── node-7 (full-1)   # 172.20.0.17
```

---

## Test Runner Script (run.sh)

### Main Execution Flow

```bash
./tests/run.sh [OPTIONS]

Options:
  --e2e           # Run E2E tests (network initialization)
  --functional    # Run functional tests
  --clean         # Clean before running
  --keep-running  # Keep containers alive after failure (for debugging)
  --backend ARG   # stage-env (default) or docker
  --package ARG   # Custom node package path/URL
```

### Execution Steps

1. **Prerequisites Check**
   - Verify Python 3 is installed
   - Verify Docker is installed

2. **Build Local Package** (if in cellframe-node repo)
   ```bash
   # Creates test_build/cellframe-node-5.7-LOCALBUILD-dbg-amd64.deb
   cmake -DCMAKE_BUILD_TYPE=Debug -DBUILD_TESTS=On ..
   make -j$(nproc) cellframe-node
   cpack -G DEB
   ```

3. **Update stage-env.cfg**
   - Sets `node_source.type = local`
   - Sets `node_source.local_path` to built package

4. **Start Network**
   ```bash
   ./stage-env/stage-env --config=stage-env.cfg start --wait
   ```
   - Generates node configurations from templates
   - Builds Docker image (if not exists)
   - Starts Docker containers
   - Executes Phase 1 genesis scenario
   - Executes Phase 2 genesis scenario

5. **Run Tests** (if --e2e or --functional)
   ```bash
   ./stage-env/stage-env run-tests --no-start-network [TEST_DIRS...] [--keep-running]
   ```

6. **Stop Network** (unless --keep-running)
   ```bash
   ./stage-env/stage-env --config=stage-env.cfg stop
   ```

### Key Variables

- `STAGE_ENV_WRAPPER`: Path to `tests/stage-env/stage-env` CLI
- `STAGE_ENV_CONFIG`: Path to `tests/stage-env.cfg`
- `TEST_BUILD_DIR`: Build directory for local package
- `DEB_PACKAGE`: Path to generated .deb package
- `KEEP_RUNNING`: Flag to keep containers alive after failure

---

## Two Testing Backends

### 1. stage-env Backend (Default, New)

**Purpose**: Modern Python-based testing framework with declarative scenarios

**Advantages**:
- Declarative YAML scenarios
- Better error handling and logging
- Snapshot management for faster testing
- Integrated debugging tools

**Key Components**:
- `src/network/manager.py`: Network lifecycle management
- `src/scenarios/executor.py`: Scenario execution engine
- `src/docker/compose.py`: Docker Compose wrapper
- `src/config/generator.py`: Configuration generation from templates

**Usage**:
```bash
./run.sh              # Uses stage-env by default
./run.sh --clean      # Clean and rebuild
./run.sh --keep-running  # Keep containers for debugging
```

### 2. docker Backend (tests-in-docker, Legacy)

**Purpose**: Reference implementation that is known to work

**Location**: `../../tests-in-docker/testnet.sh`

**Key Difference**: Uses older cellframe-node version (5.3) where automatic bootstrap key creation doesn't exist

**Usage**:
```bash
./run.sh --backend docker
./run.sh --backend docker --package /path/to/package.deb
```

**Why It Works**: Version 5.3 doesn't have automatic bootstrap validator key creation in ESBocs, so there's no conflict with `srv_stake order create`.

---

## Network Genesis Process

### Overview

Genesis happens in two phases:
1. **Phase 1**: Initialize zerochain (DAG-PoA) with ROOT nodes, create token and emission
2. **Phase 2**: Initialize mainchain (ESBocs) with MASTER nodes, create genesis block

### Phase 1: Zerochain Genesis (phase1_zerochain.yml)

**Location**: `tests/stage-env/scenarios/genesis/phase1_zerochain.yml`

**Steps** (simplified):

1. **Start ROOT nodes with seed_mode=ON**
   ```yaml
   - config: "cellframe-node"
     nodes: [root-1, root-2, root-3, master-1]
     set:
       seed_mode: "true"
   ```

2. **Wait for network links**
   ```yaml
   - network_wait: links_established
     nodes: [root-1, root-2, root-3]
     timeout: 120s
   ```

3. **Create certificates** (via bash script)
   ```bash
   # ROOT nodes (1,2,3): create node-addr and pvt.stagenet.root.N certificates
   for i in 1 2 3; do
     docker exec cellframe-stage-node-${i} cellframe-node-tool cert create node-addr sig_dil
     docker exec cellframe-stage-node-${i} cellframe-node-tool cert create pvt.stagenet.root.$((i-1)) sig_dil
     # Create public certificate
     docker exec cellframe-stage-node-${i} cellframe-node-tool cert create_cert_pkey \
       pvt.stagenet.root.$((i-1)) stagenet.root.$((i-1))
     # Copy public cert to shared CA
     docker cp cellframe-stage-node-${i}:/opt/cellframe-node/var/lib/ca/stagenet.root.$((i-1)).dcert \
       ./cache/configs/shared/ca/
   done
   
   # MASTER nodes (4,5,6): create node-addr and pvt.stagenet.master.N certificates
   for i in 4 5 6; do
     idx=$((i-4))
     docker exec cellframe-stage-node-${i} cellframe-node-tool cert create node-addr sig_dil
     docker exec cellframe-stage-node-${i} cellframe-node-tool cert create pvt.stagenet.master.${idx} sig_dil
     docker exec cellframe-stage-node-${i} cellframe-node-tool cert create_cert_pkey \
       pvt.stagenet.master.${idx} stagenet.master.${idx}
     docker cp cellframe-stage-node-${i}:/opt/cellframe-node/var/lib/ca/stagenet.master.${idx}.dcert \
       ./cache/configs/shared/ca/
   done
   ```
   
   **CRITICAL**: Certificates must be copied to `./cache/configs/shared/ca/` which is mounted as `/opt/cellframe-node/share/ca:ro` in all containers

4. **Create fee wallet**
   ```yaml
   - cli: "wallet new -w fee_collector"
     node: root-1
   - cli: "wallet info -w fee_collector"
     node: root-1
     save_wallet: fee_addr
   ```

5. **Token declaration**
   ```yaml
   - cli: "token_decl -token TCELL -chain zerochain -total_supply 1000000.0e+18 
           -decimals 18 -signs_emission 2 -signs_total 3 
           -certs stagenet.root.pvt.0,stagenet.root.pvt.1,stagenet.root.pvt.2"
     node: root-1
     save_hash: token_hash
   ```

6. **Token emission**
   ```yaml
   - cli: "token_emit -chain zerochain -token TCELL -emission_value 1000000.0e+18 
           -addr {{fee_addr}} -certs stagenet.root.pvt.0,stagenet.root.pvt.1,stagenet.root.pvt.2"
     node: root-1
     save_hash: emission_hash
   ```

7. **Set static_genesis_event in configs**
   ```yaml
   - config: "stagenet/zerochain"
     nodes: [root-1, root-2, root-3, master-1, master-2, master-3]
     set:
       static_genesis_event: "{{token_hash}}"
       is_static_genesis_event: "true"
   ```

8. **Create validator order** (CRITICAL TIMING)
   ```yaml
   # CRITICAL: Create order BEFORE restart (following tests-in-docker pattern)
   - cli: "srv_stake order create -net stagenet -value 0.05e+18 -cert stagenet.master.pvt.0"
     node: master-1
     expect: success
   ```

9. **Restart ALL nodes**
   ```yaml
   - docker_op: restart
     services: [root-1, root-2, root-3, master-1, master-2, master-3]
   ```

10. **Create wallets for all master nodes**
    ```yaml
    - loop:
        items: [0, 1, 2]
        variable: master_idx
        steps:
          - set: master_node="master-{{master_idx+1}}"
          - set: wallet_name="stagenet_master_{{master_idx}}"
          - cli: "wallet new -w {{wallet_name}}"
            node: "{{master_node}}"
    ```

### Phase 2: Mainchain Genesis (phase2_esbocs.yml)

**Location**: `tests/stage-env/scenarios/genesis/phase2_esbocs.yml`

**Steps** (simplified):

1. **Set blocks-sign-cert for master-1**
   ```yaml
   - config: "stagenet"
     nodes: [master-1]
     set:
       blocks_sign_cert: "stagenet.master.pvt.0"
   ```

2. **Restart MASTER nodes**
   ```yaml
   - docker_op: restart
     services: [master-1, master-2, master-3]
   ```

3. **Create genesis transaction**
   ```yaml
   - cli: "tx_create -net stagenet -chain main -token TCELL 
           -emission_chain main -from_emission {{emission_hash}} 
           -value 10.0e+54 -to_addr {{fee_addr}} -fee 5.0e+18 
           -cert stagenet.master.pvt.0"
     node: master-1
     save_hash: genesis_tx_hash
   ```

4. **Wait for genesis block creation** (180s)
   ```yaml
   - wait: "180s"
   ```

5. **Verify genesis block**
   ```yaml
   - cli: "block list -net stagenet -chain main"
     node: master-1
     save_hash: genesis_block_hash
     expect: success
   ```

6. **Set static_genesis_block in config**
   ```yaml
   - config: "stagenet/main"
     nodes: [master-1, master-2, master-3]
     set:
       static_genesis_block: "{{genesis_block_hash}}"
       is_static_genesis_block: "true"
   ```

---

## Critical Issues and Solutions

### Issue 1: Docker Image Conflict

**Symptom**:
```
target node-5: failed to solve: image "docker.io/library/cf-node:debug-latest": already exists
```

**Root Cause**: Multiple services trying to build the same Docker image simultaneously in `docker-compose.generated.yml`

**Solution**:
```bash
# Pre-build the image before starting containers
cd tests/stage-env
docker build -f Dockerfile.cellframe \
  --build-arg BUILD_TYPE=debug \
  --build-arg CELLFRAME_VERSION=latest \
  -t cf-node:debug-latest .
```

**Prevention**: The `run.sh` script now handles this automatically

### Issue 2: Missing [condb] Section

**Symptom**:
```
[ERR] [chain_net] No networks initialized!
Network stagenet not found
```

**Root Cause**: Missing `[condb]` section in `cellframe-node.cfg.j2` template

**Solution**: Add to `tests/stage-env/config/templates/base/cellframe-node.cfg.j2`:
```ini
[condb]
path=../etc/network
```

### Issue 3: Certificate Not Found

**Symptom**:
```
Can't open cert file '/opt/cellframe-node/var/lib/ca/stagenet.root.1.dcert'
Can't find cert "stagenet.root.1.pub"
```

**Root Cause**: Bash script in `phase1_zerochain.yml` was not copying public certificates to shared CA directory

**Solution**: The bash script must:
1. Dynamically find `STAGE_ENV_DIR` (could be `.`, `stage-env`, or `tests/stage-env`)
2. Resolve absolute path for `HOST_SHARED_CA`
3. Copy public `.dcert` files from container to host's shared CA
4. Handle "file already exists" errors (exit codes 68 and 145)

**Key Code**:
```bash
# Find stage-env directory
if [ -f "docker-compose.generated.yml" ]; then
  STAGE_ENV_DIR="."
elif [ -f "stage-env/docker-compose.generated.yml" ]; then
  STAGE_ENV_DIR="stage-env"
elif [ -f "tests/stage-env/docker-compose.generated.yml" ]; then
  STAGE_ENV_DIR="tests/stage-env"
else
  echo "ERROR: Cannot find stage-env directory!"
  exit 1
fi

HOST_SHARED_CA="$(cd "${STAGE_ENV_DIR}/cache/configs/shared/ca" && pwd)"

# Copy certificate (allow "already exists" errors)
docker cp cellframe-stage-node-${i}:/opt/cellframe-node/var/lib/ca/stagenet.root.${idx}.dcert \
  "${HOST_SHARED_CA}/" || [ $? -eq 68 ]
```

### Issue 4: Bootstrap Validator Keys Conflict (MOST CRITICAL)

**Symptom**:
```
[MSG] [dap_chain_cs_esbocs] add validator addr ABCD::EF00::0000::0000, signing addr ...
[*] [dap_chain_net_srv_stake_pos_delegate] Added key with fingerprint 0x... for node ABCD::EF00::0000::0000
[ERR] [dap_json_rpc_errors] Code error: 7 message: Can't compose the order
[ERR] [dap_chain_cs_esbocs] No valid order found was signed by this validator delegated key. Switch off validator mode.
```

Result: `block list -net stagenet -chain main` returns `have blocks: 0`

**Root Cause**: 
- Cellframe-node version 5.7 automatically creates "bootstrap validator keys" with fake address `ABCD::EF00::0000::0000` when `poa_mode=false` (default)
- These bootstrap keys conflict with real `srv_stake order create` command
- The order cannot be composed because the node already has a delegated key for the fake address

**Why tests-in-docker Works**:
- Uses older version (5.3) where automatic bootstrap key creation doesn't exist
- No `poa_mode` parameter in `main.cfg`

**Solution**: Add `poa_mode=true` to `tests/stage-env/config/templates/chains/main.cfg.j2`:

```jinja2
[esbocs]
consensus_debug=true
poa_mode=true  # Prevents automatic bootstrap key creation
min_validators_count=1
validators_addrs=[ABCD::EF00::0000::0000]
auth_certs_prefix=stagenet.master
```

**Code Reference** (`dap_chain_cs_esbocs.c:368-375`):
```c
if (!l_esbocs_pvt->poa_mode) { // auth certs in PoA mode will be first PoS validators keys
    dap_hash_fast_t l_stake_tx_hash = {};
    uint256_t l_weight = dap_chain_net_srv_stake_get_allowed_min_value(a_chain->net_id);
    dap_pkey_t *l_pkey = dap_pkey_from_enc_key(l_cert_cur->enc_key);
    dap_chain_net_srv_stake_key_delegate(l_net, &l_signing_addr, &l_stake_tx_hash,
                                        l_weight, &l_signer_node_addr, l_pkey);
    DAP_DELETE(l_pkey);
}
```

### Issue 5: Order Creation Timing

**Symptom**: Order created but lost after restart

**Solution**: Following tests-in-docker pattern (testnet.sh:181):
- Create `srv_stake order create` BEFORE full network restart
- This happens in Phase 1, after `static_genesis_event` is set
- Order persists through restart

**Wrong**:
```yaml
- docker_op: restart
- cli: "srv_stake order create"  # TOO LATE
```

**Correct**:
```yaml
- cli: "srv_stake order create"  # BEFORE restart
- docker_op: restart
```

---

## Configuration Files

### stage-env.cfg

**Location**: `tests/stage-env.cfg`

**Key Sections**:

```ini
[node_source]
type = local  # or "remote"
local_path = /path/to/cellframe-node-5.7-LOCALBUILD-dbg-amd64.deb

[network]
name = stagenet
nodes_count = 7
root_nodes_count = 3
master_nodes_count = 3
full_nodes_count = 1

[docker]
build_type = debug
network_subnet = 172.20.0.0/24
base_ip = 172.20.0.10

[snapshot]
mode = filesystem  # or "squashfs"
auto_create_on_startup = true
genesis_stage = full  # or "phase1" or "none"
```

### Jinja2 Templates

**Location**: `tests/stage-env/config/templates/`

**Structure**:
```
templates/
├── base/
│   └── cellframe-node.cfg.j2     # Main node configuration
├── chains/
│   ├── zerochain.cfg.j2           # DAG-PoA chain (ROOT nodes)
│   └── main.cfg.j2                # ESBocs chain (MASTER nodes)
└── networks/
    └── stagenet.cfg.j2            # Network-level configuration
```

**Key Template Variables**:
- `{{ node_id }}`: Node number (1-7)
- `{{ node_role }}`: "root", "master", or "full"
- `{{ node_ip }}`: IP address
- `{{ seed_mode }}`: "true" or "false"
- `{{ blocks_sign_cert }}`: Certificate name for block signing
- `{{ static_genesis_event }}`: Hash of genesis event (zerochain)
- `{{ static_genesis_block }}`: Hash of genesis block (mainchain)

### Generated Configurations

**Location**: `tests/stage-env/cache/configs/`

**Structure**:
```
cache/configs/
├── node1/
│   ├── cellframe-node.cfg         # Generated from template
│   └── network/stagenet/
│       ├── stagenet.cfg
│       ├── zerochain.cfg
│       └── main.cfg
├── node2/
...
└── shared/
    └── ca/                         # Shared certificate authority
        ├── stagenet.root.0.dcert   # Public certificates
        ├── stagenet.root.1.dcert
        ├── stagenet.master.0.dcert
        └── ...
```

### docker-compose.generated.yml

**Location**: `tests/stage-env/docker-compose.generated.yml`

**Key Points**:
- Dynamically generated by Python code
- All nodes use same Docker image: `cf-node:${BUILD_TYPE}-${CELLFRAME_VERSION}`
- Each node has unique volumes mounted:
  - Config: `./cache/configs/nodeN/...`
  - Data: `./cache/data/nodeN/...`
  - Shared CA: `./cache/configs/shared/ca:/opt/cellframe-node/share/ca:ro` (read-only)

---

## Certificates and Keys

### Certificate Types

1. **node-addr Certificate**
   - Type: `sig_dil` (Dilithium signature)
   - Purpose: Node identity
   - Created for: All nodes
   - Location: `/opt/cellframe-node/var/lib/ca/node-addr.dcert`

2. **Private Validator Certificates**
   - Names:
     - ROOT: `pvt.stagenet.root.0`, `pvt.stagenet.root.1`, `pvt.stagenet.root.2`
     - MASTER: `pvt.stagenet.master.0`, `pvt.stagenet.master.1`, `pvt.stagenet.master.2`
   - Type: `sig_dil`
   - Purpose: Sign events/blocks, create orders
   - Contains: Private and public keys

3. **Public Validator Certificates**
   - Names: `stagenet.root.N`, `stagenet.master.N`
   - Created from: Private certificates using `cert create_cert_pkey`
   - Purpose: Shared across network for verification
   - Location: 
     - In container: `/opt/cellframe-node/var/lib/ca/`
     - Shared: `./cache/configs/shared/ca/` → `/opt/cellframe-node/share/ca:ro`

### Certificate Creation Commands

```bash
# Create private certificate with node address and signature key
cellframe-node-tool cert create node-addr sig_dil

# Create private validator certificate
cellframe-node-tool cert create pvt.stagenet.root.0 sig_dil

# Extract public certificate from private
cellframe-node-tool cert create_cert_pkey pvt.stagenet.root.0 stagenet.root.0
```

**Exit Codes**:
- `68`: Certificate already exists (can be ignored)
- `145`: Public certificate already created from private (can be ignored)

### Certificate Loading

**When**: At node startup

**Where**: `dap_cert_add_folder()` in `dap_cert.c`

**Process**:
1. Scan `/opt/cellframe-node/var/lib/ca/` for `*.dcert` files
2. Scan `/opt/cellframe-node/share/ca/` for `*.dcert` files
3. Load each certificate into memory
4. Certificates created AFTER startup won't be loaded until restart

**Critical**: This is why `blocks-sign-cert` configuration and restart must happen in Phase 2 (after certificate creation)

---

## ESBocs Consensus

### What is ESBocs?

**ESBocs** (Extended Scalable Byzantine Ordered Consensus) is the consensus algorithm for mainchain (block production).

### Key Parameters

```ini
[esbocs]
consensus_debug=true
poa_mode=true                      # CRITICAL: Prevents bootstrap key creation
min_validators_count=1
validators_addrs=[ABCD::EF00::0000::0000]  # Placeholder addresses
auth_certs_prefix=stagenet.master  # Certificate prefix for validators
blocks-sign-cert=stagenet.master.pvt.0     # Specific cert for block signing
new_round_delay=5
round_start_sync_timeout=5
round_attempts_max=2
round_attempt_timeout=5
```

### Validator Key Types

1. **Auth Certificates** (poa_mode=true)
   - Defined by `auth_certs_prefix`
   - Example: `stagenet.master.pvt.0`, `stagenet.master.pvt.1`, etc.
   - Used directly as validator signing keys
   - No automatic bootstrap key creation

2. **Bootstrap Keys** (poa_mode=false, VERSION 5.7+)
   - Automatically created at startup
   - Fake node address: `ABCD::EF00::0000::0000`
   - Weight: `1.0` (minimum stake)
   - **Problem**: Conflicts with `srv_stake order create`
   - **Solution**: Use `poa_mode=true`

3. **Delegated Keys** (from srv_stake order create)
   - Created by: `srv_stake order create -cert <cert_name>`
   - Stored in: `srv_stake` service database
   - Used for: PoS validator participation
   - Requires: Private certificate with signing key

### Block Signing Certificate

**Parameter**: `blocks-sign-cert=stagenet.master.pvt.0`

**Purpose**: Specifies which certificate to use for signing blocks

**Timing**:
- Must be set AFTER certificate creation
- Must be set BEFORE mainchain initialization
- Requires node restart to take effect

**Why Phase 2?**: ESBocs loads `blocks-sign-cert` during mainchain initialization. If set in Phase 1, the certificate might not exist yet or ESBocs might not load it properly.

### srv_stake order create

**Command**:
```bash
cellframe-node-cli srv_stake order create \
  -net stagenet \
  -value 0.05e+18 \
  -cert stagenet.master.pvt.0
```

**Purpose**: Create a validator order (stake delegation)

**Requirements**:
1. Certificate `stagenet.master.pvt.0` must exist
2. Certificate must contain private key
3. Certificate must be loaded in memory
4. Token and emission must exist in ledger
5. No conflicting bootstrap keys (use `poa_mode=true`)

**Error Codes**:
- `7`: "Can't compose the order" - Usually due to signing key issues or bootstrap key conflicts
- Check logs for: `dap_chain_net_srv_stake_verify_key_and_node()` errors

**Timing** (Critical):
- Create order AFTER: `token_decl`, `token_emit`, `static_genesis_event` set
- Create order BEFORE: Full network restart
- Create order BEFORE: Phase 2 mainchain initialization

### Genesis Block Creation

**Process**:
1. Master-1 creates genesis transaction (`tx_create -emission_chain main -from_emission`)
2. Transaction enters mempool
3. ESBocs consensus validates transaction
4. ESBocs creates block with transaction
5. Block is signed using `blocks-sign-cert`
6. Block propagates to other validators

**Requirements**:
- At least one validator order must exist
- `blocks-sign-cert` must be set and loaded
- No "Switch off validator mode" errors in logs

**Verification**:
```bash
cellframe-node-cli block list -net stagenet -chain main
# Expected: "have blocks: 1" (or more)
# Genesis block hash: 0x[64 hex characters]
```

---

## Debugging Commands

### Check Container Status

```bash
# List running containers
docker ps | grep cellframe-stage-node

# Check container logs
docker logs cellframe-stage-node-4  # master-1

# Follow logs in real-time
docker logs -f cellframe-stage-node-4
```

### Access Node CLI

```bash
# Execute CLI command
docker exec cellframe-stage-node-4 cellframe-node-cli net -net stagenet get status

# Interactive shell
docker exec -it cellframe-stage-node-4 bash
# Inside container:
cellframe-node-cli help
cellframe-node-cli net -net stagenet get status
cellframe-node-cli block list -net stagenet -chain main
```

### Check Certificates

```bash
# List certificates in container
docker exec cellframe-stage-node-4 ls -la /opt/cellframe-node/var/lib/ca/
docker exec cellframe-stage-node-4 ls -la /opt/cellframe-node/share/ca/

# Check certificate details
docker exec cellframe-stage-node-4 cellframe-node-tool cert dump pvt.stagenet.master.0

# Copy certificate from container
docker cp cellframe-stage-node-4:/opt/cellframe-node/var/lib/ca/pvt.stagenet.master.0.dcert /tmp/
```

### Check Stake Orders

```bash
# List stake orders
docker exec cellframe-stage-node-4 cellframe-node-cli srv_stake order list -net stagenet

# Check node keys
docker exec cellframe-stage-node-4 cellframe-node-cli node keys

# Check wallet
docker exec cellframe-stage-node-4 cellframe-node-cli wallet list -net stagenet
docker exec cellframe-stage-node-4 cellframe-node-cli wallet info -w stagenet_master_0 -net stagenet
```

### Search Logs for Issues

```bash
# Check for bootstrap keys (should be NONE if poa_mode=true)
docker logs cellframe-stage-node-4 2>&1 | grep "add validator addr ABCD::EF00"
docker logs cellframe-stage-node-4 2>&1 | grep "Added key.*fingerprint.*ABCD::EF00"

# Check for order creation
docker logs cellframe-stage-node-4 2>&1 | grep "srv_stake order create"
docker logs cellframe-stage-node-4 2>&1 | grep "Can't compose the order"

# Check for validator mode
docker logs cellframe-stage-node-4 2>&1 | grep "Switch off validator"
docker logs cellframe-stage-node-4 2>&1 | grep "No valid order found"

# Check for certificate loading
docker logs cellframe-stage-node-4 2>&1 | grep "Cert.*loaded"
docker logs cellframe-stage-node-4 2>&1 | grep "blocks-sign-cert"

# Check for genesis block
docker logs cellframe-stage-node-4 2>&1 | grep -E "genesis|block.*created"
```

### Debug with GDB

```bash
# Install GDB in container (if not already)
docker exec cellframe-stage-node-4 apt-get update
docker exec cellframe-stage-node-4 apt-get install -y gdb

# Find cellframe-node process
docker exec cellframe-stage-node-4 pgrep -f cellframe-node

# Attach GDB to process
docker exec -it cellframe-stage-node-4 gdb -p $(docker exec cellframe-stage-node-4 pgrep -f cellframe-node)

# In GDB:
(gdb) break dap_chain_net_srv_stake_order_create
(gdb) break dap_chain_cs_esbocs_init
(gdb) continue
(gdb) backtrace
(gdb) info locals
```

### Dump Logs to Host

```bash
# The test framework automatically dumps logs on failure to /tmp/
ls -la /tmp/cellframe-stage-node-*.log

# Manual dump
docker logs cellframe-stage-node-4 2>&1 | tee /tmp/master-1.log

# Search all saved logs
grep -E "Can't compose|No valid order" /tmp/cellframe-stage-node-*.log
```

### Check Network State

```bash
# Check if nodes are online
for i in {1..6}; do
  echo "Node $i:"
  docker exec cellframe-stage-node-$i cellframe-node-cli net -net stagenet get status
done

# Check peer connections
docker exec cellframe-stage-node-4 cellframe-node-cli net -net stagenet link list

# Check chain state
docker exec cellframe-stage-node-4 cellframe-node-cli dag event list -net stagenet -chain zerochain
docker exec cellframe-stage-node-4 cellframe-node-cli block list -net stagenet -chain main
```

### Clean and Restart

```bash
# Stop all containers
docker stop $(docker ps -q --filter "name=cellframe-stage-node")

# Remove containers
docker rm $(docker ps -aq --filter "name=cellframe-stage-node")

# Remove Docker image
docker rmi cf-node:debug-latest

# Clean cache
cd tests/stage-env
rm -rf cache/configs cache/data

# Clean snapshots
rm -rf ../testing/snapshots/*

# Full restart
cd ../..
./tests/run.sh --clean --keep-running
```

---

## Version Differences

### Cellframe Node 5.3 (tests-in-docker)

**Characteristics**:
- No automatic bootstrap validator key creation
- ESBocs works with `poa_mode` implicitly false
- `srv_stake order create` works without conflicts

**Config** (`main.cfg`):
```ini
[esbocs]
consensus_debug=true
min_validators_count=1
auth_certs_prefix=foobar.master
validators_addrs=[ABCD::EF00::0000::0000]
# NO poa_mode parameter
```

### Cellframe Node 5.7 (stage-env, CURRENT)

**Characteristics**:
- Automatic bootstrap validator key creation when `poa_mode=false`
- Bootstrap keys conflict with `srv_stake order create`
- Requires `poa_mode=true` to prevent bootstrap key creation

**Config** (`main.cfg.j2`):
```ini
[esbocs]
consensus_debug=true
poa_mode=true  # REQUIRED to prevent bootstrap keys
min_validators_count=1
auth_certs_prefix=stagenet.master
validators_addrs=[ABCD::EF00::0000::0000]
blocks-sign-cert={{ blocks_sign_cert }}  # Set in Phase 2
```

**Code Change** (`dap_chain_cs_esbocs.c`):
```c
// Lines 368-375: Bootstrap key creation logic
if (!l_esbocs_pvt->poa_mode) { // auth certs in PoA mode will be first PoS validators keys
    dap_hash_fast_t l_stake_tx_hash = {};
    uint256_t l_weight = dap_chain_net_srv_stake_get_allowed_min_value(a_chain->net_id);
    dap_pkey_t *l_pkey = dap_pkey_from_enc_key(l_cert_cur->enc_key);
    dap_chain_net_srv_stake_key_delegate(l_net, &l_signing_addr, &l_stake_tx_hash,
                                        l_weight, &l_signer_node_addr, l_pkey);
    DAP_DELETE(l_pkey);
}
```

### Migration Path

To make stage-env work like tests-in-docker with version 5.7:

1. Add `poa_mode=true` to `main.cfg.j2`
2. Keep order creation in Phase 1 (before restart)
3. Set `blocks-sign-cert` in Phase 2 (after certificates exist)
4. Ensure certificate copying happens correctly in Phase 1

---

## Common Pitfalls

### 1. Forgetting --keep-running

**Problem**: Containers stop after failure, logs are lost

**Solution**: Always use `--keep-running` when debugging
```bash
./tests/run.sh --keep-running
```

### 2. Wrong Working Directory in Bash Scripts

**Problem**: Bash scripts in scenarios fail to find files

**Solution**: Always dynamically determine `STAGE_ENV_DIR`:
```bash
if [ -f "docker-compose.generated.yml" ]; then
  STAGE_ENV_DIR="."
elif [ -f "stage-env/docker-compose.generated.yml" ]; then
  STAGE_ENV_DIR="stage-env"
elif [ -f "tests/stage-env/docker-compose.generated.yml" ]; then
  STAGE_ENV_DIR="tests/stage-env"
fi
```

### 3. Certificate Not Loaded

**Problem**: Certificate exists on disk but not in memory

**Solution**: 
- Certificates must exist BEFORE node startup
- Or node must be restarted after certificate creation
- Use `docker logs` to verify: `grep "Cert.*loaded"`

### 4. Old Snapshots

**Problem**: Old snapshot with incorrect config is restored

**Solution**: Delete old snapshots before testing
```bash
rm -rf tests/testing/snapshots/*
./tests/run.sh --clean
```

### 5. Order Creation Timing

**Problem**: Order created after restart, gets lost

**Solution**: Create order BEFORE restart in Phase 1
```yaml
# Correct order:
- cli: "srv_stake order create ..."
- docker_op: restart
```

### 6. Bootstrap Keys Not Prevented

**Problem**: Bootstrap keys still created despite configuration

**Solution**: 
- Verify `poa_mode=true` in generated `main.cfg`
- Check logs for absence of "add validator addr ABCD::EF00"
- Restart from clean state if needed

---

## Quick Reference Commands

```bash
# Start tests
./tests/run.sh --keep-running

# Check if Phase 1 passed
tail -100 /tmp/final_test.log | grep "Phase 1"

# Check if Phase 2 passed
tail -100 /tmp/final_test.log | grep "Phase 2"

# Check for genesis block
docker exec cellframe-stage-node-4 cellframe-node-cli block list -net stagenet -chain main

# Check for bootstrap keys (should be empty)
docker logs cellframe-stage-node-4 2>&1 | grep "ABCD::EF00"

# Check for order creation
docker logs cellframe-stage-node-4 2>&1 | grep "srv_stake order"

# Check poa_mode in config
docker exec cellframe-stage-node-4 cat /opt/cellframe-node/etc/network/stagenet/main.cfg | grep poa_mode

# Full cleanup and restart
docker stop $(docker ps -aq --filter "name=cellframe-stage")
docker rm $(docker ps -aq --filter "name=cellframe-stage")
docker rmi cf-node:debug-latest
cd tests/stage-env && rm -rf cache/configs cache/data && cd ../..
rm -rf tests/testing/snapshots/*
./tests/run.sh --clean --keep-running
```

---

## Success Criteria

A successful test run should show:

1. **Phase 1 Complete**:
   ```
   [info] Scenario completed: 76/76 steps passed
   [info] zerochain_genesis_complete
   ```

2. **No Bootstrap Keys**:
   ```
   # grep "ABCD::EF00" in logs should return NOTHING
   ```

3. **Order Created Successfully**:
   ```
   [info] CLI: srv_stake order create ...
   # No "Can't compose the order" error
   ```

4. **Phase 2 Complete**:
   ```
   [info] Scenario completed: X/X steps passed
   [info] mainchain_genesis_complete
   ```

5. **Genesis Block Exists**:
   ```
   docker exec cellframe-stage-node-4 cellframe-node-cli block list -net stagenet -chain main
   # Output: stagenet.main with filter - none, have blocks: 1 (or more)
   # Shows: hash: 0x[64 hex chars]
   ```

6. **No Validator Mode Errors**:
   ```
   # No "Switch off validator mode" in logs
   # No "No valid order found" in logs
   ```

---

## For AI Agents

When debugging test failures:

1. **First, check which phase failed**: Phase 1 (zerochain) or Phase 2 (mainchain)

2. **For Phase 1 failures**:
   - Check certificate creation and copying
   - Verify network connectivity
   - Check token_decl and token_emit succeeded

3. **For Phase 2 failures (most common)**:
   - Check for bootstrap keys in logs (grep "ABCD::EF00")
   - Verify `poa_mode=true` in `main.cfg`
   - Check order creation logs
   - Verify `blocks-sign-cert` is set
   - Check genesis transaction succeeded

4. **Always use `--keep-running`** when debugging to keep containers alive

5. **Compare with tests-in-docker** if behavior differs

6. **Check version differences** if code behavior seems inconsistent

7. **Read node logs** (docker logs) for actual errors, don't trust only test framework output

---

## Final Notes

This testing system is complex because it:
1. Simulates a real multi-node blockchain network
2. Handles two-phase genesis (DAG-PoA + ESBocs)
3. Manages certificates, keys, and consensus
4. Deals with version-specific behavior changes

The key to success is understanding:
- **Timing**: When to create certificates, orders, and restart nodes
- **Bootstrap keys**: How they conflict and how to prevent them
- **Certificate loading**: When certificates are loaded into memory
- **Version differences**: How 5.3 vs 5.7 behaves differently

Always start debugging with node logs and work backwards to understand what's happening at the consensus layer.

