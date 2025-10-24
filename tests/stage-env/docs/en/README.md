# Stage Environment - Cellframe Node Testing Infrastructure

**Autonomous system for E2E testing of blockchain applications**

Stage Environment is a full-featured infrastructure for running and testing Cellframe Node in an isolated Docker environment. The system is completely autonomous, easily portable, and doesn't require deep programming knowledge to write tests.

## 🎯 Features

- ✅ **YAML Scenarios** - write tests in declarative language without programming
- ✅ **Automation** - build, run, test, collect artifacts
- ✅ **Docker Isolation** - each test in clean environment
- ✅ **Flexible Topologies** - from 1 node to complex networks
- ✅ **Artifacts & Reports** - automatic collection of logs, core dumps, PDF report generation
- ✅ **Rich CLI** - beautiful interface with colored output and progress bars

## 🚀 Quick Start

### Minimal Example

```bash
# 1. Start test network (automatically installs dependencies)
cd tests
./stage-env/stage-env start

# 2. Check status
./stage-env/stage-env status

# 3. Run tests
./stage-env/stage-env run-tests scenarios/

# 4. Stop
./stage-env/stage-env stop
```

### Run via run.sh

```bash
# Full cycle: build + tests + reports
cd tests
./run.sh --e2e

# Results in testing/artifacts/e2e_*/reports/
```

## 📖 Documentation

### For QA Engineers

- **[Scenarios Tutorial](scenarios/Tutorial.md)** - Step-by-step learning of scenario language
- **[Scenarios Cookbook](scenarios/Cookbook.md)** - Ready recipes for common tasks
- **[Scenarios Glossary](scenarios/Glossary.md)** - Complete language reference

### For Developers

- **[Architecture](Architecture.md)** - System architecture
- **[Integration](Integration.md)** - Project integration
- **[CI/CD](CICD.md)** - CI/CD setup

## 📁 Project Structure

```
stage-env/
├── stage-env                # Bash wrapper (entry point)
├── stage_env.py             # Python CLI (Typer)
├── stage-env.cfg            # Configuration (in tests/)
│
├── src/                     # Python modules
│   ├── config/              # Configuration management
│   ├── docker/              # Docker Compose integration
│   ├── network/             # Topologies and network
│   ├── build/               # Build artifacts
│   ├── certs/               # Certificate generation
│   └── utils/               # Logging, reports, artifacts
│
├── config/                  # Configuration files
│   ├── topologies/          # Network topology templates
│   └── templates/           # Jinja2 config templates
│
├── scenarios/               # YAML test scenarios
│   ├── common/              # Reusable templates
│   └── features/            # Feature-specific tests
│
└── docs/                    # Documentation
    ├── en/                  # English docs
    ├── ru/                  # Russian docs
    └── scenarios/           # Scenarios documentation
```

## 🎨 Main Commands

```bash
# === Network Management ===
stage-env start              # Start network
stage-env start --no-wait    # Start without waiting for ONLINE
stage-env stop               # Stop network
stage-env restart            # Restart
stage-env status             # Show node status

# === Testing ===
stage-env run-tests <dir>    # Run tests from directory
stage-env run-tests test.yml # Run specific scenario

# === Monitoring ===
stage-env logs node-1        # Show node logs
stage-env logs node-1 -f     # Follow logs
stage-env exec node-1 "cmd"  # Execute command in node

# === Artifacts and Reports ===
stage-env collect-artifacts e2e --exit-code=0

# === Build ===
stage-env build              # Build Cellframe Node
stage-env build --clean      # Clean build

# === Certificates ===
stage-env certs --nodes 7    # Generate certificates

# === Cleanup ===
stage-env clean --all        # Clean everything
stage-env stop --volumes     # Stop and remove volumes
```

## 📝 Writing Tests

### Simple Test

```yaml
# scenarios/my_test.yml
name: My First Test
description: Check wallet creation

includes:
  - common/network_minimal.yml

test:
  - cli: wallet new -w test_wallet
    save: wallet_addr
  
  - cli: wallet list
    contains: test_wallet

check:
  - cli: wallet info -w test_wallet
    contains: {{wallet_addr}}
```

### Running Test

```bash
./stage-env/stage-env run-tests scenarios/my_test.yml
```

### Ready Templates

- `common/network_minimal.yml` - 1 node
- `common/network_full.yml` - 7 nodes (validators + full node)
- `common/wallet_setup.yml` - Ready wallet

## 🔧 Configuration

Main configuration in `tests/stage-env.cfg`:

```ini
[network]
name = stagenet
network_id = 0x1234

[paths]
cache_dir = ../testing/cache
artifacts_dir = ../testing/artifacts

[artifacts]
collect_node_logs = true
collect_health_logs = true
collect_crash_dumps = true
retain_days = 30

[timeouts]
startup = 600
health_check = 600
command = 30
```

## 🎯 Integration into Your Project

### Example run.sh

```bash
#!/bin/bash
set -euo pipefail

STAGE_ENV="./stage-env/stage-env"
STAGE_ENV_CONFIG="./stage-env.cfg"

# Build (optional)
# cmake -B build && make -C build

# Start network
"$STAGE_ENV" --config="$STAGE_ENV_CONFIG" start

# Run tests
"$STAGE_ENV" --config="$STAGE_ENV_CONFIG" run-tests scenarios/

# Collect artifacts
"$STAGE_ENV" --config="$STAGE_ENV_CONFIG" collect-artifacts e2e --exit-code=$?

# Stop
"$STAGE_ENV" --config="$STAGE_ENV_CONFIG" stop
```

### Topology Configuration

Create `config/topologies/my-network.json`:

```json
{
  "network": {
    "name": "mynet",
    "network_id": "0x5678"
  },
  "topology": {
    "validators": {
      "count": 5,
      "role": "validator",
      "consensus_participation": true
    },
    "full_nodes": {
      "count": 2,
      "role": "full",
      "consensus_participation": false
    }
  }
}
```

Run:

```bash
./stage-env start --topology my-network
```

## 📊 Artifacts and Reports

After each run in `testing/artifacts/<run_id>/`:

```
e2e_20251023_150000/
├── reports/
│   ├── report.md            # Markdown report
│   └── report.pdf           # PDF report (pandoc)
├── stage-env-logs/          # Stage-env logs
├── node-logs/               # Docker container logs
├── core-dumps/              # Core dumps (if any)
├── health-logs/             # Health check logs
└── summary.json             # JSON summary
```

## 🔍 Troubleshooting

### Docker Issues

```bash
# Check Docker
docker ps
docker-compose version

# Restart Docker
sudo systemctl restart docker
```

### Port Issues

```bash
# Check occupied ports
ss -tlnp | grep 8079

# Stop all containers
./stage-env stop --volumes
```

### Python Issues

```bash
# Recreate venv
rm -rf .venv
./stage-env --help  # Will create venv again
```

### Debug Logs

```bash
# Verbose mode
./stage-env --verbose start

# Specific node logs
./stage-env logs node-1 --tail 100

# All nodes status
./stage-env status
```

## 📚 Detailed Documentation

- **[Tutorial](scenarios/Tutorial.md)** - Step-by-step guide for QA
- **[Cookbook](scenarios/Cookbook.md)** - Recipes for common tasks
- **[Glossary](scenarios/Glossary.md)** - Complete language reference

## 🤝 Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Create Pull Request

## 📜 License

See LICENSE in project root.

## 🔗 Links

- [Cellframe Node](https://github.com/demlabs-cellframe/cellframe-node)
- [DAP SDK](https://github.com/demlabs-cellframe/dap-sdk)
- [Python Cellframe](https://github.com/demlabs-cellframe/python-cellframe)

---

**Language:** English | [Русский](../ru/README.md)

