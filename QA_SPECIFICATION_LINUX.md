# Cellframe Node - QA Specification for Linux

## Document Version
- **Version**: 1.0.0
- **Date**: 2025-10-03
- **Purpose**: Reference standard for QA testing and automated validation in Docker containers
- **Target OS**: Linux (Debian/Ubuntu based distributions)

---

## Table of Contents
1. [Installation Requirements](#1-installation-requirements)
2. [Installation Process](#2-installation-process)
3. [Post-Installation Verification](#3-post-installation-verification)
4. [Service Management](#4-service-management)
5. [Configuration Files](#5-configuration-files)
6. [Network Configuration](#6-network-configuration)
7. [CLI Commands Reference](#7-cli-commands-reference)
8. [Logging and Monitoring](#8-logging-and-monitoring)
9. [Expected Runtime Behavior](#9-expected-runtime-behavior)
10. [Performance Metrics](#10-performance-metrics)
11. [Error Conditions](#11-error-conditions)
12. [Python Plugins](#12-python-plugins)

---

## 1. Installation Requirements

### 1.1 System Requirements
- **OS**: Debian 9/10/11 or Ubuntu 18.04+
- **Architecture**: amd64, arm64 (armhf deprecated for Python plugins)
- **Minimum RAM**: 2GB
- **Minimum Disk Space**: 5GB
- **Network**: Internet connection required for package installation

### 1.2 Required Dependencies
Package dependencies that must be installed:
```bash
dpkg (>=1.17)
bash (>=4)
less
pv
psmisc
logrotate
irqbalance
xz-utils
```

### 1.3 Build Dependencies (for source build)
```bash
build-essential
cmake
dpkg-dev
libz-dev
libmagic-dev
libsqlite3-dev
traceroute
debconf-utils
xsltproc
libpq-dev
```

---

## 2. Installation Process

### 2.1 Installation from Repository

#### Step 1: Add DemLabs Repository
Create file `/etc/apt/sources.list.d/demlabs.list`:

**For Debian 11 (Bullseye):**
```
deb https://debian.pub.demlabs.net/public bullseye main
```

**For Debian 10 (Buster):**
```
deb https://debian.pub.demlabs.net/public buster main
```

**For Ubuntu 18.04 (Bionic):**
```
deb https://debian.pub.demlabs.net/public bionic main
```

#### Step 2: Add GPG Key
```bash
wget https://debian.pub.demlabs.net/public/public-key.gpg
sudo apt-key add public-key.gpg
```

#### Step 3: Install Package
```bash
sudo apt-get update
sudo apt-get install cellframe-node
```

**Expected Output:**
- Package download progress
- Debconf configuration questions (see section 2.2)
- Post-installation script execution
- Service activation message

### 2.2 Installation Configuration Questions

During installation, the following questions should be asked (via debconf):

1. **Auto online**: `true` (default) - Node goes online automatically after start
2. **Debug mode**: `false` (default) - Production mode, set `true` for testing
3. **Debug stream headers**: `false` (default) - Only enable for deep debugging
4. **Accept connections**: `false` (default) - Enable to accept incoming connections
5. **Server address**: `0.0.0.0` (default) - Listen on all interfaces
6. **Server port**: `8079` (default) - Can be changed to 80 or 443
7. **Backbone network**: `on` (default) - Enable Mainnet
8. **KelVPN network**: `on` (default) - Enable KelVPN network
9. **Node role**: `full` (default) - Full node functionality

### 2.3 Expected Installation Output

The installation process should complete with the following steps:

```
[*] Creating run, lib, var dirs....
[!] Enabling logrotate
[!] Set exec permissions
[+] Found pip: /opt/cellframe-node/python/bin/pip3
[+] Found python: /opt/cellframe-node/python/bin/python3.10
[*] Installing Python packages...
[+] Successfully installed: pycfhelpers-*.whl
[+] Successfully installed: pycftools-*.whl
[!] Run cellframe-config for configuration...
[!] Set cfg permissions
[!] Setting up cellframe-node as service
[!] Starting up cellframe-node
[!] Done
```

**Installation Exit Codes:**
- `0`: Success
- `-1`: Invalid path
- `-2`: Can't create directory
- `-3`: Can't init common functions
- `-4`: Can't init config
- `-5`: Can't open general config

### 2.4 Installed Files Structure

After successful installation, the following structure must exist:

```
/opt/cellframe-node/
├── bin/
│   ├── cellframe-node              # Main daemon executable
│   ├── cellframe-node-cli          # CLI client
│   ├── cellframe-node-tool         # Utility tool
│   └── cellframe-node-config       # Configuration tool
├── etc/
│   ├── cellframe-node.cfg          # Main configuration file
│   ├── cellframe-node.cfg.d/       # Config fragments
│   │   └── logrotate.cfg
│   └── network/                    # Network configurations
│       ├── Backbone/               # Mainnet config
│       │   ├── main.cfg
│       │   └── chain-0.cfg
│       ├── KelVPN/                 # KelVPN config
│       │   ├── main.cfg
│       │   └── chain-0.cfg
│       ├── riemann/                # Testnet (disabled by default)
│       ├── raiden/                 # Testnet (disabled by default)
│       ├── mileena/                # Testnet (disabled by default)
│       └── subzero/                # Devnet (disabled by default)
├── var/
│   ├── log/
│   │   └── cellframe-node.log      # Main log file
│   ├── run/
│   │   ├── cellframe-node.pid      # PID file
│   │   └── node_cli                # CLI socket
│   ├── lib/
│   │   ├── wallet/                 # Wallet storage
│   │   ├── global_db/              # Global database
│   │   ├── network/                # Network data storage
│   │   │   ├── Backbone/
│   │   │   └── KelVPN/
│   │   └── plugins/                # Python plugins
│   └── var/
│       └── plugins/
├── python/
│   ├── bin/
│   │   ├── python3.10 (or 3.11)    # Python interpreter
│   │   └── pip3                    # Python package manager
│   └── lib/
│       └── python3.10/             # Python libraries
│           └── site-packages/
│               ├── pycfhelpers/
│               ├── pycftools/
│               └── interfaces/
├── share/
│   ├── cellframe-node.service      # Systemd service file
│   ├── default.setup               # Default setup script
│   ├── configs/                    # Config templates
│   ├── ca/                         # Certificate authorities
│   ├── wheels/                     # Python wheel packages (if prebuild)
│   ├── logrotate/                  # Logrotate configuration
│   ├── profile.d/
│   │   └── cellframe-node.sh       # Environment variables
│   └── doc/
│       └── changelog
```

---

## 3. Post-Installation Verification

### 3.1 File System Check

Verify that all critical directories and files exist:

```bash
# Check main directories
test -d /opt/cellframe-node/bin || echo "FAIL: bin directory missing"
test -d /opt/cellframe-node/etc || echo "FAIL: etc directory missing"
test -d /opt/cellframe-node/var || echo "FAIL: var directory missing"
test -d /opt/cellframe-node/python || echo "FAIL: python directory missing"

# Check executables
test -x /opt/cellframe-node/bin/cellframe-node || echo "FAIL: cellframe-node not executable"
test -x /opt/cellframe-node/bin/cellframe-node-cli || echo "FAIL: cellframe-node-cli not executable"
test -x /opt/cellframe-node/bin/cellframe-node-tool || echo "FAIL: cellframe-node-tool not executable"

# Check configuration files
test -f /opt/cellframe-node/etc/cellframe-node.cfg || echo "FAIL: main config missing"
test -f /opt/cellframe-node/etc/network/Backbone/main.cfg || echo "FAIL: Backbone config missing"
test -f /opt/cellframe-node/etc/network/KelVPN/main.cfg || echo "FAIL: KelVPN config missing"
```

**Expected Result**: All tests pass, no "FAIL" messages

### 3.2 Python Environment Check

```bash
# Check Python installation
/opt/cellframe-node/python/bin/python3 --version

# Check Python packages
/opt/cellframe-node/python/bin/python3 -c "import pycfhelpers; print('pycfhelpers OK')"
/opt/cellframe-node/python/bin/python3 -c "import pycftools; print('pycftools OK')"

# Check pip
/opt/cellframe-node/python/bin/pip3 list
```

**Expected Output:**
```
Python 3.10.x (or 3.11.x)
pycfhelpers OK
pycftools OK
```

### 3.3 Service Status Check

```bash
systemctl status cellframe-node
```

**Expected Output:**
```
● cellframe-node.service - Cellframe Node
     Loaded: loaded (/opt/cellframe-node/share/cellframe-node.service; enabled; vendor preset: enabled)
     Active: active (running) since [timestamp]
   Main PID: [pid] (cellframe-node)
      Tasks: [number]
     Memory: [size]
        CPU: [time]
     CGroup: /system.slice/cellframe-node.service
             └─[pid] /opt/cellframe-node/bin/cellframe-node
```

**Key Indicators:**
- Status: `active (running)`
- Loaded: `enabled`
- Process should be running with valid PID

### 3.4 Process Check

```bash
ps aux | grep cellframe-node
```

**Expected Output:**
```
root  [PID]  [CPU]  [MEM]  [VSZ]  [RSS]  ?  [STAT]  [START]  [TIME]  /opt/cellframe-node/bin/cellframe-node
```

**Process Characteristics:**
- User: `root`
- Working directory: `/opt/cellframe-node`
- Command: `/opt/cellframe-node/bin/cellframe-node`

### 3.5 Network Socket Check

```bash
ss -tlnp | grep cellframe
# or
netstat -tlnp | grep cellframe
```

**Expected Output (if server enabled):**
```
tcp   LISTEN  0  128  0.0.0.0:8079  0.0.0.0:*  users:(("cellframe-node",pid=[PID],fd=[FD]))
tcp   LISTEN  0  128  127.0.0.1:8080  0.0.0.0:*  users:(("cellframe-node",pid=[PID],fd=[FD]))
```

**Expected Sockets:**
- Port `8079`: Main server port (if `server.enabled=true`)
- Port `8080`: Notify server (local only)
- Unix socket: `/opt/cellframe-node/var/run/node_cli` (CLI communication)

### 3.6 Version Check

```bash
/opt/cellframe-node/bin/cellframe-node -version
```

**Expected Output:**
```
CellframeNode, [VERSION], [BUILD_DATE], [GIT_HASH]
```

Example:
```
CellframeNode, 5.2-106, 03.10.2025, a1b2c3d
```

---

## 4. Service Management

### 4.1 Systemd Service Configuration

Service file location: `/opt/cellframe-node/share/cellframe-node.service`

**Service Parameters:**
```ini
[Unit]
Description=Cellframe Node
After=network-online.target
Wants=network-online.target

[Service]
WorkingDirectory=/opt/cellframe-node
ExecStart=/opt/cellframe-node/bin/cellframe-node &
ExecStop=/bin/kill -SIGTERM $MAINPID
Restart=always
User=root
Group=root
RestartSec=10
LogNamespace=cellframe
CapabilityBoundingSet=CAP_NET_BIND_SERVICE CAP_IPC_LOCK CAP_KILL CAP_LEASE CAP_MKNOD CAP_NET_ADMIN CAP_NET_BROADCAST CAP_NET_RAW CAP_SYS_NICE CAP_SYS_RAWIO CAP_SYSLOG CAP_WAKE_ALARM CAP_SYS_RESOURCE CAP_DAC_READ_SEARCH

[Install]
WantedBy=multi-user.target
```

### 4.2 Service Commands

#### Start Service
```bash
sudo systemctl start cellframe-node
# or
sudo service cellframe-node start
# or via config tool
sudo /opt/cellframe-node/bin/cellframe-node-config -e service start
```

**Expected Result**: Service starts, exit code 0

#### Stop Service
```bash
sudo systemctl stop cellframe-node
# or
sudo service cellframe-node stop
# or via config tool
sudo /opt/cellframe-node/bin/cellframe-node-config -e service stop
```

**Expected Result**: Service stops gracefully, exit code 0

#### Restart Service
```bash
sudo systemctl restart cellframe-node
# or
sudo service cellframe-node restart
# or via config tool
sudo /opt/cellframe-node/bin/cellframe-node-config -e service restart
```

#### Check Service Status
```bash
sudo systemctl status cellframe-node
# or
sudo service cellframe-node status
# or via config tool
sudo /opt/cellframe-node/bin/cellframe-node-config -e service status
```

#### Enable Service (auto-start on boot)
```bash
sudo systemctl enable cellframe-node
# or via config tool
sudo /opt/cellframe-node/bin/cellframe-node-config -e service enable
```

#### Disable Service
```bash
sudo systemctl disable cellframe-node
# or via config tool
sudo /opt/cellframe-node/bin/cellframe-node-config -e service disable
```

### 4.3 Service Restart Behavior

**Restart Policy**: `always` with `RestartSec=10`

**Expected Behavior:**
- If node crashes, systemd will restart it after 10 seconds
- If node is manually stopped, systemd will NOT restart it
- Maximum restart attempts: unlimited

---

## 5. Configuration Files

### 5.1 Main Configuration File

**Location**: `/opt/cellframe-node/etc/cellframe-node.cfg`

**Key Sections and Default Values:**

#### [general]
```ini
debug_mode=false                    # Production mode by default
debug_dump_stream_headers=false     # Don't dump stream headers
auto_online=true                    # Auto go online after start
```

#### [server]
```ini
enabled=false                       # Server disabled by default (client mode)
listen_address=[0.0.0.0:8079]      # Listen on all interfaces, port 8079
news_url_enabled=false
bugreport_url_enabled=false
```

#### [notify_server]
```ini
listen_address=[127.0.0.1:8080]    # Local only, port 8080
```

#### [bootstrap_balancer]
```ini
dns_server=false
http_server=true                    # HTTP balancer enabled
```

#### [cli-server]
```ini
enabled=true                        # CLI server always enabled
listen-path=[../var/run/node_cli]  # Unix socket for CLI (Linux only)
listen-address=[127.0.0.1:12345]   # TCP fallback
version=1
```

#### [resources]
```ini
threads_cnt=0                       # Auto-detect CPU cores
pid_path=../var/run/cellframe-node.pid
log_file=../var/log/cellframe-node.log
wallets_path=../var/lib/wallet
ca_folders=[../var/lib/ca,../share/ca]
```

#### [global_db]
```ini
path=../var/lib/global_db
driver=mdbx                         # MDBX database driver
```

#### [plugins]
```ini
enabled=false                       # Plugins disabled by default
py_path=../var/lib/plugins         # Python plugins path
```

#### [mempool]
```ini
auto_proc=false                     # Disabled by default (requires master role)
```

#### [srv_vpn]
```ini
enabled=false                       # VPN service disabled by default
network_address=10.11.12.0
network_mask=255.255.255.0
```

### 5.2 Network Configuration Files

#### Backbone (Mainnet)
**Location**: `/opt/cellframe-node/etc/network/Backbone/main.cfg`

**Key Parameters:**
```ini
[general]
id=0x53c0rp10n                      # Network ID
network_name=Backbone
native_ticker=CELL
node-role=full                      # full, light, master, root, archive
seed_nodes_hosts=[0.root.scorpion.cellframe.net:8079,1.root.scorpion.cellframe.net:8079,2.root.scorpion.cellframe.net:8079,3.root.scorpion.cellframe.net:8079,4.root.scorpion.cellframe.net:8079]
```

**Chain Configuration**: `/opt/cellframe-node/etc/network/Backbone/chain-0.cfg`
```ini
[chain]
id=0x0000000000000002
name=main
consensus=esbocs
datum_types=[transaction,anchor]

[esbocs]
min_validators_count=1
auth_certs_prefix=scorpion.master
validators_addrs=[DFAB::CDC2::A6BA::48FB,BC53::9462::EF3A::E47D,D05E::E083::A665::37A8]
new_round_delay=30
```

#### KelVPN Network
**Location**: `/opt/cellframe-node/etc/network/KelVPN/main.cfg`

**Key Parameters:**
```ini
[general]
id=0x4b656c56504e                  # Network ID
network_name=KelVPN
native_ticker=KEL
node-role=full
seed_nodes_hosts=[0.root.kelvpn.com:8079,1.root.kelvpn.com:8079,2.root.kelvpn.com:8079]
```

#### Disabled Networks by Default
- `riemann/` - Testnet (disabled)
- `raiden/` - Testnet (disabled)
- `mileena/` - Testnet (disabled)
- `subzero/` - Devnet (disabled, .cfg.dis extension)

### 5.3 Configuration Validation

Check configuration syntax:
```bash
# Using config tool
sudo /opt/cellframe-node/bin/cellframe-node-config -e net_list all

# Check specific network
sudo /opt/cellframe-node/bin/cellframe-node-config -e net_list on
```

**Expected Output for `net_list on`:**
```
Backbone
KelVPN
```

---

## 6. Network Configuration

### 6.1 Default Active Networks

After default installation, the following networks should be enabled:

1. **Backbone** (Mainnet)
   - State: ENABLED (main.cfg exists)
   - Native Token: CELL
   - Node Role: full
   - Seed Nodes: 5 root nodes

2. **KelVPN**
   - State: ENABLED (main.cfg exists)
   - Native Token: KEL
   - Node Role: full
   - Seed Nodes: 3 root nodes

### 6.2 Network State Verification

```bash
# List all networks
sudo /opt/cellframe-node/bin/cellframe-node-cli net list

# Check Backbone status
sudo /opt/cellframe-node/bin/cellframe-node-cli net -net Backbone get status

# Check KelVPN status
sudo /opt/cellframe-node/bin/cellframe-node-cli net -net KelVPN get status
```

**Expected Output for `net list`:**
```json
{
  "networks": [
    {
      "name": "Backbone",
      "state": "NET_STATE_ONLINE",
      "active_links": 3,
      "target_state": "NET_STATE_ONLINE"
    },
    {
      "name": "KelVPN",
      "state": "NET_STATE_SYNC_CHAINS",
      "active_links": 2,
      "target_state": "NET_STATE_ONLINE"
    }
  ]
}
```

**Network States:**
- `NET_STATE_OFFLINE`: Network is offline
- `NET_STATE_LINKS_PREPARE`: Preparing to connect
- `NET_STATE_LINKS_CONNECTING`: Establishing connections
- `NET_STATE_LINKS_ESTABLISHED`: Links established
- `NET_STATE_ADDR_REQUEST`: Requesting addresses
- `NET_STATE_SYNC_GDB`: Synchronizing global database
- `NET_STATE_SYNC_CHAINS`: Synchronizing chains
- `NET_STATE_ONLINE`: Fully synchronized and online

### 6.3 Node Address

Each node gets a unique address in format: `XXXX::XXXX::XXXX::XXXX`

```bash
# Get node address for Backbone
sudo /opt/cellframe-node/bin/cellframe-node-cli net -net Backbone get status
```

**Expected Output:**
```
Network "Backbone" has state NET_STATE_ONLINE (target state NET_STATE_ONLINE), active links 3 from 4, cur node address 374C::CEB5::6740::D93B
```

### 6.4 Network Links

```bash
# List network links for Backbone
sudo /opt/cellframe-node/bin/cellframe-node-cli net -net Backbone link list
```

**Expected Output:**
```
Link uplink [node_address] address [IP:PORT] state ESTABLISHED
Link uplink [node_address] address [IP:PORT] state ESTABLISHED
Link uplink [node_address] address [IP:PORT] state ESTABLISHED
```

**Healthy Node Criteria:**
- Minimum 2 active links per network
- Link state: ESTABLISHED
- Links to seed nodes successful

---

## 7. CLI Commands Reference

### 7.1 CLI Connection

**Methods:**
1. Unix socket (Linux default): `/opt/cellframe-node/var/run/node_cli`
2. TCP/IP fallback: `127.0.0.1:12345`

**Basic Usage:**
```bash
sudo /opt/cellframe-node/bin/cellframe-node-cli [command] [options]
```

### 7.2 Help and Information Commands

#### Get Help
```bash
cellframe-node-cli help
cellframe-node-cli help [command]
```

#### Version Information
```bash
cellframe-node-cli version
```

**Expected Output:**
```
CellframeNode version: [VERSION]
Git commit: [HASH]
Build date: [DATE]
```

#### Node Information
```bash
cellframe-node-cli node dump
cellframe-node-cli node connections
```

### 7.3 Network Commands

#### List Networks
```bash
cellframe-node-cli net list
cellframe-node-cli net list chains -net <network_name>
```

#### Network Status
```bash
cellframe-node-cli net -net <network_name> get status
cellframe-node-cli net -net <network_name> get fee
cellframe-node-cli net -net <network_name> get id
```

#### Network Operations
```bash
# Go online
cellframe-node-cli net -net <network_name> go online

# Go offline
cellframe-node-cli net -net <network_name> go offline

# Synchronize
cellframe-node-cli net -net <network_name> sync all
cellframe-node-cli net -net <network_name> sync gdb
cellframe-node-cli net -net <network_name> sync chains
```

#### Network Statistics
```bash
cellframe-node-cli net -net <network_name> stats tx
cellframe-node-cli net -net <network_name> stats tps
```

#### Network Links
```bash
cellframe-node-cli net -net <network_name> link list
cellframe-node-cli net -net <network_name> link add -addr <node_address>
cellframe-node-cli net -net <network_name> link del -addr <node_address>
cellframe-node-cli net -net <network_name> link disconnect_all
```

### 7.4 Wallet Commands

#### List Wallets
```bash
cellframe-node-cli wallet list
```

**Expected Output:**
```
Available wallets:
  [wallet_name1]
  [wallet_name2]
```

#### Create New Wallet
```bash
cellframe-node-cli wallet new -w <wallet_name> [-sign <sign_type>] [-password <password>]
```

**Sign Types:**
- `sig_dil` (default) - Dilithium (quantum-safe)
- `sig_bliss` - BLISS
- `sig_tesla` - TESLA
- `sig_picnic` - Picnic

**Expected Output:**
```
Wallet '[wallet_name]' (type=sig_dil) successfully created
```

#### Wallet Info
```bash
cellframe-node-cli wallet info -w <wallet_name> -net <network_name>
cellframe-node-cli wallet info -addr <address> -net <network_name>
```

**Expected Output:**
```json
{
  "wallet": "my_wallet",
  "addr": "mJUU...aedd",
  "network": "Backbone",
  "balance": {
    "CELL": "1000.000000000"
  }
}
```

#### Wallet Outputs
```bash
cellframe-node-cli wallet outputs -w <wallet_name> -net <network_name> -token <token>
```

#### Wallet Activation (for password-protected wallets)
```bash
cellframe-node-cli wallet activate -w <wallet_name> -password <password> [-ttl <minutes>]
cellframe-node-cli wallet deactivate -w <wallet_name>
```

### 7.5 Transaction Commands

#### Create Transaction
```bash
cellframe-node-cli tx_create -net <network_name> -chain <chain_name> \
  -from_wallet <wallet_name> -to_addr <address> -token <token> -value <amount>
```

**Expected Output:**
```
transfer=Ok
tx_hash=0x4E6D540F86CD46CBFA551F219A04BA2248FF474BB795EB5B2C524299458AD709
```

#### Transaction History
```bash
# By wallet
cellframe-node-cli tx_history -w <wallet_name> -net <network_name>

# By address
cellframe-node-cli tx_history -addr <address> -net <network_name>

# By hash
cellframe-node-cli tx_history -tx <tx_hash> -net <network_name>

# All transactions
cellframe-node-cli tx_history -all -net <network_name> [-chain <chain_name>]

# Count
cellframe-node-cli tx_history -count -net <network_name>
```

**Output Options:**
- `-limit <number>`: Limit number of results
- `-offset <number>`: Skip first N results
- `-head`: Show only headers

#### Transaction Verification
```bash
cellframe-node-cli tx_verify -net <network_name> -tx <tx_hash>
```

### 7.6 Token Commands

#### List Tokens
```bash
cellframe-node-cli token list -net <network_name> [-full]
```

**Expected Output:**
```json
{
  "tokens": [
    {
      "ticker": "CELL",
      "type": "native",
      "total_supply": "1000000000.000000000",
      "decimals": 18
    },
    {
      "ticker": "KEL",
      "type": "native",
      "total_supply": "500000000.000000000",
      "decimals": 18
    }
  ]
}
```

#### Token Info
```bash
cellframe-node-cli token info -net <network_name> -name <token_ticker>
```

### 7.7 Ledger Commands

#### List Coins
```bash
cellframe-node-cli ledger list coins -net <network_name>
```

#### List Balances
```bash
cellframe-node-cli ledger list balance -net <network_name>
```

#### Ledger Info
```bash
cellframe-node-cli ledger info -hash <tx_hash> -net <network_name>
```

#### Reload Ledger Cache
```bash
cellframe-node-cli net -net <network_name> ledger reload
```

### 7.8 Node Management Commands

#### Add Node
```bash
cellframe-node-cli node add -net <network_name> [-port <port>]
```

#### Connect to Node
```bash
cellframe-node-cli node connect -net <network_name> -addr <node_address>
cellframe-node-cli node connect -net <network_name> auto
```

#### List Nodes
```bash
cellframe-node-cli node list -net <network_name> [-full]
```

#### Node Connections
```bash
cellframe-node-cli node connections [-net <network_name>]
```

#### Node Handshake
```bash
cellframe-node-cli node handshake -net <network_name> -addr <node_address>
```

#### Balancer Info
```bash
cellframe-node-cli node balancer -net <network_name>
```

### 7.9 Certificate Authority Commands

#### List CA Certificates
```bash
cellframe-node-cli net -net <network_name> ca list
```

#### Add CA Certificate
```bash
cellframe-node-cli net -net <network_name> ca add -cert <cert_name>
cellframe-node-cli net -net <network_name> ca add -hash <cert_hash>
```

#### Delete CA Certificate
```bash
cellframe-node-cli net -net <network_name> ca del -hash <cert_hash>
```

### 7.10 Mempool Commands

#### Sign File
```bash
cellframe-node-cli mempool sign -cert <priv_cert_name> -net <network_name> \
  -chain <chain_name> -file <filename>
```

#### Check Signature
```bash
cellframe-node-cli mempool check -cert <priv_cert_name> -net <network_name> \
  -file <filename>
```

### 7.11 Global DB Commands

#### List GDB
```bash
cellframe-node-cli global_db [command]
```

### 7.12 Log Commands

#### Print Log
```bash
cellframe-node-cli print_log [last <N>]
```

---

## 8. Logging and Monitoring

### 8.1 Log File Location

**Main Log File**: `/opt/cellframe-node/var/log/cellframe-node.log`

### 8.2 Log Levels

Log levels in order of verbosity:
1. `L_CRITICAL` - Critical errors (always logged)
2. `L_ERROR` - Errors
3. `L_ATT` - Attention
4. `L_WARNING` - Warnings
5. `L_NOTICE` - Notices (default production level)
6. `L_MESSAGE` - Messages
7. `L_DAP` - DAP protocol messages
8. `L_INFO` - Information
9. `L_DEBUG` - Debug messages (debug mode only)

**Debug Mode:**
- Set in config: `[general] debug_mode=true`
- Changes log level from L_NOTICE to L_DEBUG
- Produces significantly more output

### 8.3 Expected Log Messages on Startup

**Normal Startup Sequence:**

```
[L_DEBUG] Use main path: /opt/cellframe-node
[L_ATT] *** NORMAL MODE ***
[L_DAP] *** CellFrame Node version: 5.2-106 ***
[L_NOTICE] Log rotation every 1440 min enabled, max log file size 100 MB
[L_INFO] Automatic mempool processing disabled
[L_INFO] No enabled server, working in client mode only
[L_NOTICE] Loading python plugins
[L_NOTICE] Network "Backbone" initialized
[L_NOTICE] Network "KelVPN" initialized
[L_INFO] Network "Backbone" going online
[L_INFO] Network "KelVPN" going online
[L_INFO] Network "Backbone" state changed to NET_STATE_LINKS_PREPARE
[L_INFO] Network "KelVPN" state changed to NET_STATE_LINKS_PREPARE
[L_INFO] Connected to seed node 0.root.scorpion.cellframe.net:8079
[L_INFO] Network "Backbone" state changed to NET_STATE_SYNC_GDB
[L_INFO] Network "Backbone" state changed to NET_STATE_SYNC_CHAINS
[L_INFO] Network "Backbone" state changed to NET_STATE_ONLINE
```

**Key Startup Messages:**
1. Version information
2. Mode (NORMAL or DEBUG)
3. Module initialization messages
4. Network initialization
5. Link establishment
6. Synchronization progress
7. Online status

### 8.4 Error Messages

**Common Error Messages and Meanings:**

| Error Message | Severity | Meaning | Action |
|--------------|----------|---------|--------|
| `Can't init encryption module` | CRITICAL | Crypto init failed | Check system libraries |
| `Can't init global db module` | CRITICAL | Database init failed | Check disk space, permissions |
| `Can't open general config` | CRITICAL | Config file missing/invalid | Reinstall or restore config |
| `dap_server is already running` | ERROR | Another instance running | Stop existing instance |
| `Can't connect to seed node` | WARNING | Network connectivity issue | Check internet connection |
| `Chain sync failed` | WARNING | Sync issue | Retry sync |
| `Invalid transaction` | INFO | TX validation failed | Check TX parameters |

### 8.5 Log Rotation

**Configuration**: `/opt/cellframe-node/etc/cellframe-node.cfg.d/logrotate.cfg`

**Default Settings:**
```ini
[log]
rotate_enabled=true
rotate_timeout=1440          # Minutes (24 hours)
rotate_size=100              # MB
```

**Expected Behavior:**
- Logs rotate every 24 hours OR when reaching 100MB
- Old logs compressed: `cellframe-node.log.1.gz`
- Maximum log files: 7 (one week)

**Logrotate Configuration**: `/opt/cellframe-node/share/logrotate/cellframe-node`

```
/opt/cellframe-node/var/log/cellframe-node.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
}
```

### 8.6 Monitoring Metrics

#### System Metrics to Monitor

1. **CPU Usage**
   - Normal: 5-20% during sync
   - Normal: 1-5% when idle online
   - Alert: >50% sustained

2. **Memory Usage**
   - Normal: 200-500 MB
   - Normal during sync: 500-1000 MB
   - Alert: >2 GB

3. **Disk I/O**
   - Normal during sync: High
   - Normal when online: Low
   - Alert: Sustained high I/O when idle

4. **Network Traffic**
   - Normal during sync: 1-10 MB/s
   - Normal when online: 10-100 KB/s
   - Alert: No traffic for >5 minutes

#### Node Health Metrics

```bash
# Check node is responding
/opt/cellframe-node/bin/cellframe-node-cli version

# Check network status
/opt/cellframe-node/bin/cellframe-node-cli net list

# Check active links
/opt/cellframe-node/bin/cellframe-node-cli node connections
```

**Healthy Node Indicators:**
- CLI responds within 1 second
- At least 2 active network links per network
- Network state: NET_STATE_ONLINE
- No errors in last 100 log lines

---

## 9. Expected Runtime Behavior

### 9.1 Node Lifecycle Stages

#### Stage 1: Initialization (0-10 seconds)
**Expected Behavior:**
- Process starts
- Configuration files loaded
- Modules initialized
- PID file created
- Log file opened

**Expected Log Messages:**
```
[L_DEBUG] Use main path: /opt/cellframe-node
[L_ATT] *** NORMAL MODE ***
[L_DAP] *** CellFrame Node version: [VERSION] ***
```

#### Stage 2: Network Preparation (10-30 seconds)
**Expected Behavior:**
- Networks initialized
- Certificates loaded
- DNS resolution of seed nodes
- Link preparation

**Expected Log Messages:**
```
[L_NOTICE] Network "Backbone" initialized
[L_NOTICE] Network "KelVPN" initialized
[L_INFO] Network "Backbone" going online
```

#### Stage 3: Link Establishment (30-60 seconds)
**Expected Behavior:**
- Connecting to seed nodes
- Handshake with peers
- Link establishment
- State: NET_STATE_LINKS_CONNECTING → NET_STATE_LINKS_ESTABLISHED

**Expected Log Messages:**
```
[L_INFO] Network "Backbone" state changed to NET_STATE_LINKS_PREPARE
[L_INFO] Connected to seed node 0.root.scorpion.cellframe.net:8079
[L_INFO] Link established with node [ADDRESS]
```

#### Stage 4: GDB Synchronization (1-5 minutes)
**Expected Behavior:**
- Syncing global database
- Downloading node lists, CA certs, etc.
- State: NET_STATE_SYNC_GDB

**Expected Log Messages:**
```
[L_INFO] Network "Backbone" state changed to NET_STATE_SYNC_GDB
[L_INFO] GDB sync progress: [percentage]%
```

#### Stage 5: Chain Synchronization (5-30 minutes)
**Expected Behavior:**
- Syncing blockchain data
- Downloading blocks/events
- Validating chains
- State: NET_STATE_SYNC_CHAINS

**Expected Log Messages:**
```
[L_INFO] Network "Backbone" state changed to NET_STATE_SYNC_CHAINS
[L_INFO] Chain "main" sync: [blocks] blocks synchronized
```

#### Stage 6: Online (steady state)
**Expected Behavior:**
- Fully synchronized
- Maintaining connections
- Processing new blocks
- State: NET_STATE_ONLINE

**Expected Log Messages:**
```
[L_INFO] Network "Backbone" state changed to NET_STATE_ONLINE
[L_INFO] New block received: [hash]
```

### 9.2 Normal Operation Indicators

**Healthy Node Criteria:**

1. **Process Running**
   - PID file exists: `/opt/cellframe-node/var/run/cellframe-node.pid`
   - Process is running
   - No zombie processes

2. **Network Status**
   - Backbone: NET_STATE_ONLINE
   - KelVPN: NET_STATE_ONLINE
   - Active links: ≥2 per network

3. **Resource Usage**
   - CPU: <10% average
   - Memory: 200-800 MB
   - Disk I/O: Low when idle

4. **Log Health**
   - No CRITICAL errors in last hour
   - No more than 10 ERROR messages per hour
   - Regular heartbeat messages

5. **CLI Responsiveness**
   - Commands respond within 1 second
   - No timeout errors

### 9.3 First-Time Sync Timeline

**Expected Timeline for Fresh Node:**

| Time | Stage | Networks | Description |
|------|-------|----------|-------------|
| 0-10s | Init | - | Process starts, config loaded |
| 10-30s | Prepare | Backbone, KelVPN | Networks initialized |
| 30-60s | Connect | Backbone, KelVPN | Links established |
| 1-5min | GDB Sync | Backbone | Global DB syncing |
| 2-6min | GDB Sync | KelVPN | Global DB syncing |
| 5-15min | Chain Sync | Backbone | Main chain syncing |
| 6-20min | Chain Sync | KelVPN | Main chain syncing |
| 15-30min | Online | Backbone | Fully synchronized |
| 20-35min | Online | KelVPN | Fully synchronized |

**Note**: Times may vary based on:
- Network speed
- CPU performance
- Blockchain size
- Number of seed nodes available

### 9.4 Subsequent Startups

**Expected Timeline for Already-Synced Node:**

| Time | Stage | Description |
|------|-------|-------------|
| 0-10s | Init | Process starts |
| 10-20s | Prepare | Networks initialized |
| 20-40s | Connect | Links established |
| 40-60s | Catch-up | Syncing new data since last run |
| 1-2min | Online | Fully operational |

### 9.5 Memory Growth Pattern

**Expected Memory Usage Over Time:**

```
Startup:       100-200 MB
After 1 hour:  200-400 MB
After 24 hours: 300-600 MB
After 1 week:  400-800 MB
Steady state:  500-1000 MB
```

**Alert Conditions:**
- Memory >2 GB: Investigate memory leak
- Memory growth >100 MB/hour: Abnormal

---

## 10. Performance Metrics

### 10.1 Baseline Performance Metrics

**Hardware Reference:**
- CPU: 4 cores @ 2.4 GHz
- RAM: 4 GB
- Disk: SSD
- Network: 100 Mbps

**Expected Performance:**

| Metric | Value | Notes |
|--------|-------|-------|
| Startup time | 30-60s | First links established |
| Full sync time | 15-30 min | Fresh node, both networks |
| CLI response time | <1s | Simple commands |
| Block processing | 10-50/s | During sync |
| Transaction throughput | 100-1000 tx/s | Network dependent |
| Memory footprint | 300-800 MB | Steady state |
| CPU usage (idle) | 1-5% | Online, no sync |
| CPU usage (sync) | 20-50% | During chain sync |
| Disk space | 2-5 GB | After full sync |
| Network bandwidth (idle) | 10-50 KB/s | Maintenance traffic |
| Network bandwidth (sync) | 1-10 MB/s | Chain synchronization |

### 10.2 Transaction Performance

**Transaction Verification:**
- Simple transfer: <100ms
- Complex smart contract: <500ms

**Transaction Creation:**
- Wallet → CLI: <50ms
- CLI → Node: <100ms
- Node → Mempool: <200ms

**Transaction Propagation:**
- Mempool → Network: <1s
- Network-wide propagation: 5-30s

### 10.3 Database Performance

**Global DB Operations:**
- Read: <10ms per record
- Write: <50ms per record
- Sync: 100-1000 records/s

**Chain DB Operations:**
- Block read: <10ms
- Block write: <100ms
- Chain validation: 10-50 blocks/s

### 10.4 Network Performance

**Link Quality Metrics:**
- Ping to seed nodes: <100ms
- Packet loss: <1%
- Link uptime: >99%

**Synchronization Speed:**
- GDB sync: 1000-5000 records/s
- Chain sync: 10-50 blocks/s
- Full network sync: 15-30 minutes

### 10.5 Performance Testing Commands

#### Test CLI Response Time
```bash
time /opt/cellframe-node/bin/cellframe-node-cli version
# Expected: <1 second
```

#### Test Network Latency
```bash
/opt/cellframe-node/bin/cellframe-node-cli net -net Backbone link list
# Check ping times to links
```

#### Test Transaction Performance
```bash
time /opt/cellframe-node/bin/cellframe-node-cli tx_history -count -net Backbone
# Expected: <2 seconds
```

#### Monitor Resource Usage
```bash
# CPU and Memory
top -p $(pgrep cellframe-node)

# Disk I/O
iotop -p $(pgrep cellframe-node)

# Network I/O
nethogs -p $(pgrep cellframe-node)
```

---

## 11. Error Conditions

### 11.1 Critical Errors (Exit Immediately)

**Exit Code**: `-56` to `-82`

| Exit Code | Error | Cause | Solution |
|-----------|-------|-------|----------|
| -1 | Invalid path | g_sys_dir_path invalid | Fix installation path |
| -2 | Can't create directory | Permission or disk space | Check permissions, disk space |
| -3 | Can't init common | Log file issue | Check /var/log permissions |
| -4 | Can't init config | Config path wrong | Check /etc directory |
| -5 | Can't open config | Config file missing | Reinstall or restore |
| -56 | Encryption init failed | Crypto library issue | Reinstall dependencies |
| -58 | Global DB init failed | Database issue | Check disk space, permissions |
| -59 | Mempool init failed | Memory issue | Check available memory |
| -60 | Chain init failed | Chain data corrupt | Remove chain data, resync |

### 11.2 Warning Conditions (Continue Running)

**Non-Fatal Errors:**

| Condition | Severity | Action |
|-----------|----------|--------|
| Can't connect to seed | WARNING | Retry with other seeds |
| Chain sync failed | WARNING | Retry sync |
| Link dropped | NOTICE | Reconnect |
| Invalid transaction | INFO | Reject transaction |
| Python plugin failed | WARNING | Continue without plugin |

### 11.3 Recovery Procedures

#### Scenario 1: Node Won't Start

**Symptoms:**
- Service fails to start
- Exit code != 0
- No process running

**Diagnosis:**
```bash
# Check service status
sudo systemctl status cellframe-node

# Check logs
sudo tail -n 100 /opt/cellframe-node/var/log/cellframe-node.log

# Check config
sudo /opt/cellframe-node/bin/cellframe-node-config -e net_list all
```

**Solutions:**
1. Check configuration files
2. Check permissions
3. Check disk space
4. Reinstall package

#### Scenario 2: Node Stuck in SYNC State

**Symptoms:**
- Network state: NET_STATE_SYNC_* for >1 hour
- No progress in logs
- Active links present

**Diagnosis:**
```bash
# Check network status
sudo /opt/cellframe-node/bin/cellframe-node-cli net -net Backbone get status

# Check links
sudo /opt/cellframe-node/bin/cellframe-node-cli net -net Backbone link list
```

**Solutions:**
1. Restart node
2. Force resync: `net -net Backbone sync all -mode all`
3. Clear database and resync
4. Check network connectivity

#### Scenario 3: High Memory Usage

**Symptoms:**
- Memory >2 GB
- System swapping
- Node slow to respond

**Diagnosis:**
```bash
# Check memory
ps aux | grep cellframe-node

# Check for memory leaks
valgrind /opt/cellframe-node/bin/cellframe-node
```

**Solutions:**
1. Restart node
2. Update to latest version
3. Report bug if persistent

#### Scenario 4: No Network Connectivity

**Symptoms:**
- No active links
- Can't sync
- Network state: OFFLINE or LINKS_PREPARE

**Diagnosis:**
```bash
# Check internet connectivity
ping 8.8.8.8

# Check DNS resolution
nslookup 0.root.scorpion.cellframe.net

# Check firewall
sudo iptables -L -n | grep 8079
```

**Solutions:**
1. Check firewall rules
2. Check DNS settings
3. Check seed node availability
4. Try different seed nodes

#### Scenario 5: Database Corruption

**Symptoms:**
- Errors reading/writing database
- Chain validation errors
- Crashes on specific operations

**Diagnosis:**
```bash
# Check database integrity
ls -lh /opt/cellframe-node/var/lib/global_db/
ls -lh /opt/cellframe-node/var/lib/network/Backbone/
```

**Solutions:**
1. Stop node
2. Backup database
3. Remove corrupted database:
   ```bash
   sudo rm -rf /opt/cellframe-node/var/lib/global_db/*
   sudo rm -rf /opt/cellframe-node/var/lib/network/Backbone/*
   sudo rm -rf /opt/cellframe-node/var/lib/network/KelVPN/*
   ```
4. Restart node (will resync)

### 11.4 Health Check Script

**Basic Health Check:**

```bash
#!/bin/bash

# Check process
if ! pgrep -f cellframe-node > /dev/null; then
    echo "FAIL: Node process not running"
    exit 1
fi

# Check service
if ! systemctl is-active --quiet cellframe-node; then
    echo "FAIL: Service not active"
    exit 1
fi

# Check CLI response
if ! timeout 5 /opt/cellframe-node/bin/cellframe-node-cli version > /dev/null; then
    echo "FAIL: CLI not responding"
    exit 1
fi

# Check network status
STATUS=$(/opt/cellframe-node/bin/cellframe-node-cli net -net Backbone get status)
if ! echo "$STATUS" | grep -q "NET_STATE_ONLINE"; then
    echo "WARNING: Backbone not online"
fi

echo "OK: Node healthy"
exit 0
```

---

## 12. Python Plugins

### 12.1 Python Environment

**Python Version:**
- Linux x86_64: Python 3.10.x
- Linux aarch64: Python 3.11.x

**Python Location:**
```
/opt/cellframe-node/python/
├── bin/
│   ├── python3.10 (or python3.11)
│   └── pip3
└── lib/
    └── python3.10/ (or python3.11/)
        └── site-packages/
```

### 12.2 Required Python Packages

**Core Packages:**
1. **pycfhelpers**
   - Version: 1.0.3+
   - Purpose: Helper functions for Cellframe plugins
   - Location: `site-packages/pycfhelpers/`

2. **pycftools**
   - Version: 1.0.0+
   - Purpose: Tools for Cellframe plugins
   - Location: `site-packages/pycftools/`

### 12.3 Python Environment Verification

```bash
# Check Python version
/opt/cellframe-node/python/bin/python3 --version

# Check pip
/opt/cellframe-node/python/bin/pip3 --version

# List installed packages
/opt/cellframe-node/python/bin/pip3 list

# Verify pycfhelpers
/opt/cellframe-node/python/bin/python3 -c "import pycfhelpers; print(pycfhelpers.__version__)"

# Verify pycftools
/opt/cellframe-node/python/bin/python3 -c "import pycftools; print(pycftools.__version__)"
```

**Expected Output:**
```
Python 3.10.x (or 3.11.x)
pip 22.x or higher
pycfhelpers (1.0.3+)
pycftools (1.0.0+)
```

### 12.4 Plugin Directory

**Plugin Location**: `/opt/cellframe-node/var/lib/plugins/`

**Plugin Structure:**
```
/opt/cellframe-node/var/lib/plugins/
├── my_plugin/
│   ├── __init__.py
│   ├── manifest.json
│   └── main.py
```

### 12.5 Plugin Configuration

**Configuration**: `/opt/cellframe-node/etc/cellframe-node.cfg`

```ini
[plugins]
enabled=false                    # Enable/disable plugins
py_path=../var/lib/plugins      # Plugin directory
```

**Enable Plugins:**
```bash
sudo /opt/cellframe-node/bin/cellframe-node-config -e config cellframe-node plugins enabled ensure true
```

### 12.6 Plugin Verification

**Check Plugin Loading:**
```bash
# Check logs for plugin loading
sudo grep "python plugin" /opt/cellframe-node/var/log/cellframe-node.log

# List loaded plugins
sudo /opt/cellframe-node/bin/cellframe-node-cli plugin list
```

**Expected Log Messages:**
```
[L_NOTICE] Loading python plugins
[L_INFO] Python plugin [plugin_name] loaded successfully
```

---

## 13. Automated Testing Checklist

### 13.1 Pre-Flight Checks (Before Installation)

- [ ] System meets minimum requirements
- [ ] Internet connectivity available
- [ ] Sufficient disk space (>5GB free)
- [ ] No existing cellframe-node process running

### 13.2 Installation Checks

- [ ] Repository added successfully
- [ ] GPG key imported
- [ ] Package installs without errors
- [ ] Debconf questions answered
- [ ] Post-install script completes successfully
- [ ] Exit code is 0

### 13.3 File System Checks

- [ ] `/opt/cellframe-node/bin/` exists
- [ ] All executables present and executable
- [ ] `/opt/cellframe-node/etc/` exists
- [ ] Main config file exists
- [ ] Network configs exist (Backbone, KelVPN)
- [ ] `/opt/cellframe-node/var/` directory structure created
- [ ] Python environment present
- [ ] Log file created

### 13.4 Configuration Checks

- [ ] Main config is valid syntax
- [ ] Network configs are valid
- [ ] Default networks enabled (Backbone, KelVPN)
- [ ] Other networks disabled
- [ ] Database driver set (mdbx)
- [ ] CLI server enabled
- [ ] Python environment configured

### 13.5 Service Checks

- [ ] Systemd service file exists
- [ ] Service is enabled
- [ ] Service starts successfully
- [ ] Process is running
- [ ] PID file created
- [ ] Service restart works
- [ ] Service auto-restart on crash works

### 13.6 Network Checks

- [ ] CLI responds to commands
- [ ] Networks listed correctly
- [ ] Backbone network present
- [ ] KelVPN network present
- [ ] Networks go online within 2 minutes
- [ ] Links establish to seed nodes
- [ ] Node gets unique address
- [ ] Minimum 2 links per network

### 13.7 Functional Checks

- [ ] Can create wallet
- [ ] Can list wallets
- [ ] Can get wallet info
- [ ] Can list networks
- [ ] Can get network status
- [ ] Can list tokens
- [ ] Can view transaction history
- [ ] Can sync network manually

### 13.8 Performance Checks

- [ ] Startup time <60s
- [ ] Memory usage <1GB
- [ ] CPU usage <50% during sync
- [ ] CLI response <1s
- [ ] Logs written correctly
- [ ] No critical errors in logs

### 13.9 Python Environment Checks

- [ ] Python interpreter works
- [ ] pip works
- [ ] pycfhelpers imports successfully
- [ ] pycftools imports successfully
- [ ] Python version correct (3.10 or 3.11)

### 13.10 Cleanup Checks

- [ ] Can stop service cleanly
- [ ] Can disable service
- [ ] Can uninstall package
- [ ] Files removed on uninstall
- [ ] Config preserved (optional)

---

## 14. Docker Testing Strategy

### 14.1 Docker Test Container

**Base Image**: `debian:bullseye` or `ubuntu:22.04`

**Test Workflow:**
1. Start clean container
2. Install dependencies
3. Add repository
4. Install cellframe-node
5. Run all checks from Section 13
6. Report results
7. Clean up

### 14.2 Test Automation

**Test Script Structure:**
```bash
#!/bin/bash

# Function definitions for each check
check_installation() { ... }
check_filesystem() { ... }
check_service() { ... }
check_networks() { ... }
check_functionality() { ... }

# Main test execution
run_all_tests() {
    check_installation || exit 1
    check_filesystem || exit 2
    check_service || exit 3
    check_networks || exit 4
    check_functionality || exit 5
    echo "ALL TESTS PASSED"
}

run_all_tests
```

### 14.3 Expected Docker Test Output

**Success Case:**
```
[TEST] Installation: PASS
[TEST] Filesystem: PASS
[TEST] Configuration: PASS
[TEST] Service: PASS
[TEST] Networks: PASS
[TEST] Functionality: PASS
[TEST] Performance: PASS
[TEST] Python: PASS
=================================
ALL TESTS PASSED (8/8)
Exit code: 0
```

**Failure Case:**
```
[TEST] Installation: PASS
[TEST] Filesystem: PASS
[TEST] Configuration: PASS
[TEST] Service: FAIL - Service won't start
  - Expected: active (running)
  - Actual: failed
  - Log: Can't init global db module
=================================
TESTS FAILED (3/8)
Exit code: 3
```

### 14.4 Continuous Monitoring

**Production Monitoring:**
1. Process health check every 1 minute
2. Network status check every 5 minutes
3. Memory usage check every 5 minutes
4. Log error analysis every 10 minutes
5. Full health check every 30 minutes

---

## 15. Appendix

### 15.1 Exit Codes Reference

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Already running |
| -1 | Invalid path |
| -2 | Directory creation failed |
| -3 | Common init failed |
| -4 | Config init failed |
| -5 | Config open failed |
| -56 | Encryption init failed |
| -58 | Global DB init failed |
| -59 | Mempool init failed |
| -60 | Chain init failed |
| -61 | Wallet init failed |
| -62 | DAG consensus init failed |
| -63 | PoA consensus init failed |
| -65 | Chain network init failed |
| -66 | Network service init failed |
| -67 | Service order init failed |
| -69 | ESBOCS consensus init failed |
| -70 | VPN service init failed |
| -71 | Nonconsensus init failed |
| -72 | VPN client init failed |
| -73 | GeoIP init failed |
| -81 | Encryption HTTP init failed |
| -82 | Stream init failed |
| -83 | Stream CTL init failed |

### 15.2 File Permissions

**Expected Permissions:**

```
/opt/cellframe-node/bin/*               755 (executable)
/opt/cellframe-node/etc/**/*.cfg        666 (rw-rw-rw-)
/opt/cellframe-node/etc/                777 (drwxrwxrwx)
/opt/cellframe-node/var/                755 (drwxr-xr-x)
/opt/cellframe-node/var/log/*           644 (rw-r--r--)
/opt/cellframe-node/python/bin/*        755 (executable)
```

### 15.3 Network Ports

| Port | Protocol | Purpose | Bind Address |
|------|----------|---------|--------------|
| 8079 | TCP | Node P2P communication | 0.0.0.0 (if server enabled) |
| 8080 | TCP | Notify server | 127.0.0.1 (local only) |
| 12345 | TCP | CLI server (fallback) | 127.0.0.1 (local only) |

**Firewall Rules (if server enabled):**
```bash
sudo ufw allow 8079/tcp
```

### 15.4 Useful Commands Summary

```bash
# Service management
sudo systemctl {start|stop|restart|status} cellframe-node
sudo systemctl {enable|disable} cellframe-node

# Quick status check
sudo /opt/cellframe-node/bin/cellframe-node-cli net list
sudo /opt/cellframe-node/bin/cellframe-node-cli node connections

# View logs
sudo tail -f /opt/cellframe-node/var/log/cellframe-node.log
sudo journalctl -u cellframe-node -f

# Network operations
sudo /opt/cellframe-node/bin/cellframe-node-cli net -net Backbone go online
sudo /opt/cellframe-node/bin/cellframe-node-cli net -net Backbone sync all

# Configuration
sudo /opt/cellframe-node/bin/cellframe-node-config -e net_list all
sudo /opt/cellframe-node/bin/cellframe-node-config -e network Backbone ensure on

# Wallet operations
sudo /opt/cellframe-node/bin/cellframe-node-cli wallet list
sudo /opt/cellframe-node/bin/cellframe-node-cli wallet new -w mywallet
sudo /opt/cellframe-node/bin/cellframe-node-cli wallet info -w mywallet -net Backbone

# Debugging
sudo /opt/cellframe-node/bin/cellframe-node-cli print_log last 100
sudo /opt/cellframe-node/bin/cellframe-node-cli node dump
```

---

## Document Change Log

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | 2025-10-03 | Initial comprehensive specification | AI Assistant |

---

## Notes

- This document is a living standard and should be updated as the software evolves
- All test cases should be automated where possible
- Docker test container should run this full test suite
- Performance metrics are based on reference hardware; adjust for different configurations
- Report any deviations from this specification as potential bugs


