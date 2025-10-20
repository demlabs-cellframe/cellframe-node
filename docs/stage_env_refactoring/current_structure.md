# Current tests/stage-env Structure Analysis

**Analysis Date:** 2025-10-19  
**QEVM References Count:** 278 occurrences (excluding cache/data/logs)  
**Total Files:** ~40 files + configuration templates

## 📁 Directory Structure

```
tests/stage-env/
├── cache/                      # ❌ MIXED: Generated + versioned files
│   └── certs/                 # Generated certificates (should not be versioned)
│       └── pki-config.json
├── certs/                      # ❌ DUPLICATE: Empty dirs (redundant with cache/)
├── configs/                    # ⚠️ NEEDS REFACTORING
│   ├── common/
│   ├── node1-3/               # ❌ HARDCODED: Static node configs
│   └── templates/
│       ├── cellframe-node.cfg.d/
│       │   ├── disable-production-networks.cfg
│       │   ├── enable-qevm-stagenet.cfg    # 🔴 QEVM-specific
│       │   └── enable-server.cfg
│       ├── chains/
│       │   └── main.cfg
│       ├── qevm-plugin.cfg                  # 🔴 QEVM-specific
│       └── qevm-stagenet.cfg                # 🔴 QEVM-specific
├── data/                       # ❌ TEMPORARY: Node data (should be in cache/)
│   └── node1-3/
├── logs/                       # ❌ TEMPORARY: Log files (should be in cache/)
│   └── node1-3/
├── monitoring/                 # ❌ TEMPORARY: Monitoring data (should be in cache/)
├── results/                    # ❌ TEMPORARY: Test results (should be in cache/)
├── scripts/                    # ✅ GOOD: Bash scripts (needs Python migration)
│   ├── build-manager.sh       # 🔄 ~300 lines
│   ├── crash-handler.sh       # 🔄 ~150 lines
│   ├── docker-entrypoint.sh   # 🔄 ~100 lines
│   ├── health-check.sh        # 🔄 ~100 lines
│   ├── init-node.sh           # 🔄 ~200 lines
│   ├── network-manager.sh     # 🔄 ~500 lines (most complex)
│   ├── node-supervisor.sh     # 🔄 ~200 lines
│   └── update-validator-addrs.sh  # 🔄 ~80 lines
├── tests/                      # ⚠️ PYTHON: Functional tests (keep, move to tests/functional/)
│   ├── basic-connectivity.py
│   ├── consensus-test.py
│   ├── load-test.py
│   ├── requirements.txt
│   └── run-tests.sh
├── tools/                      # ⚠️ C TOOLS: Certificate generator (move to src/certs/)
│   ├── cert-generator.c
│   ├── CMakeLists.txt
│   └── dap-cert.c
├── build-and-package.sh        # 🔄 ~100 lines (to src/build/)
├── build.sh                    # 🔄 ~250 lines (to src/build/)
├── check-network.sh            # 🔄 ~80 lines (to src/network/)
├── docker-compose.yml          # ⚠️ REFACTOR: 🔴 Contains QEVM comments/vars
├── Dockerfile.builder          # ⚠️ REFACTOR: 🔴 QEVM build steps
├── Dockerfile.cellframe         # ⚠️ REFACTOR: 🔴 QEVM plugin copying
├── Dockerfile.tests            # ✅ KEEP
├── e2e_ctl.sh                  # 🔄 ~350 lines (to stage_env.py)
├── generate-all-certs.sh       # 🔄 ~150 lines (to src/certs/generator.py)
├── generate-validator-certs.sh # 🔄 ~100 lines (to src/certs/generator.py)
├── network-topology.json       # ⚠️ MOVE: to config/topologies/default.json
├── QUICK_START.md              # ⚠️ UPDATE: 🔴 Remove QEVM references
└── README.md                   # ⚠️ UPDATE: 🔴 Remove QEVM references
```

## 🔴 QEVM Specificity Issues (278 occurrences)

### Configuration Files
- `configs/templates/qevm-plugin.cfg` - QEVM plugin configuration
- `configs/templates/cellframe-node.cfg.d/enable-qevm-stagenet.cfg` - QEVM network enable
- `configs/templates/qevm-stagenet.cfg` - QEVM stagenet configuration
- `network-topology.json` - contains `"qevm-stagenet"` network name
- `docker-compose.yml` - QEVM service names, comments, variables

### Docker Files
- `Dockerfile.builder` - QEVM build steps and paths
- `Dockerfile.cellframe` - QEVM plugin installation

### Documentation
- `README.md` - 50+ QEVM references
- `QUICK_START.md` - 30+ QEVM references

### Python Tests
- `tests/*.py` - QEVM-specific terminology

### Scripts
- All bash scripts contain QEVM references in comments and variables

## 📊 Entry Points Analysis

### Main Entry Points
1. **e2e_ctl.sh** (~350 lines)
   - Main orchestrator script
   - Commands: `start`, `stop`, `status`, `build`, `clean`, `run-tests`
   - Calls: `scripts/network-manager.sh`, `scripts/build-manager.sh`, `generate-all-certs.sh`
   - **Status:** ❌ Must be replaced with `stage_env.py`

2. **scripts/network-manager.sh** (~500 lines)
   - Network topology management
   - Dynamic node creation
   - Docker Compose orchestration
   - **Status:** 🔄 Complex, needs full Python migration

3. **build.sh** (~250 lines)
   - Build orchestration
   - Artifact management
   - **Status:** 🔄 Needs Python migration to `src/build/builder.py`

### Secondary Entry Points
- `build-and-package.sh` - packaging logic
- `check-network.sh` - network health check
- `generate-all-certs.sh` - certificate generation
- `tests/run-tests.sh` - test runner

## 📦 Dependencies Analysis

### Bash Scripts Dependencies

```
e2e_ctl.sh
├── scripts/network-manager.sh
│   ├── scripts/init-node.sh
│   ├── scripts/health-check.sh
│   └── docker-compose.yml
├── scripts/build-manager.sh
├── generate-all-certs.sh
│   ├── tools/cert-generator (C binary)
│   └── generate-validator-certs.sh
└── scripts/node-supervisor.sh
    └── scripts/crash-handler.sh
```

### Docker Dependencies
- `Dockerfile.builder` → builds cellframe-node + plugin
- `Dockerfile.cellframe` → uses builder artifacts
- `Dockerfile.tests` → runs Python tests
- `docker-compose.yml` → orchestrates all services

### External Dependencies
- Docker 20.10+
- Docker Compose 2.0+
- Python 3.8+ (for tests)
- Build tools: gcc, cmake, make (in builder)

## 🎯 Current Workflow

### 1. Build Workflow
```bash
./e2e_ctl.sh build
  └→ scripts/build-manager.sh
      └→ docker-compose build builder
          └→ Dockerfile.builder (CMake build)
```

### 2. Certificate Generation
```bash
./e2e_ctl.sh start (if certs missing)
  └→ generate-all-certs.sh
      ├→ tools/cert-generator (C binary)
      └→ generate-validator-certs.sh
```

### 3. Network Startup
```bash
./e2e_ctl.sh start
  └→ scripts/network-manager.sh start
      ├→ docker-compose up (dynamic node creation)
      ├→ scripts/init-node.sh (in containers)
      ├→ scripts/docker-entrypoint.sh (container startup)
      └→ scripts/node-supervisor.sh (process monitoring)
          └→ scripts/crash-handler.sh (if crash)
```

### 4. Test Execution
```bash
./e2e_ctl.sh run-tests [paths]
  └→ tests/run-tests.sh [paths]
      └→ pytest/python3 tests/*.py
```

## 🚫 Problems Identified

### 1. **QEVM Specificity (CRITICAL)**
- 278 occurrences in 35+ files
- Hardcoded QEVM references in configs, docs, scripts
- Not generic for cellframe-node testing

### 2. **Directory Structure Issues**
- Temporary files mixed with versioned files
- `cache/` contains both generated and permanent files
- `certs/`, `data/`, `logs/`, `monitoring/`, `results/` should be under `cache/`
- `tools/` should be `src/certs/`
- No clear separation of concerns

### 3. **Bash Script Complexity**
- ~15 bash scripts totaling ~2000 lines
- Hard to maintain and test
- No type safety
- Limited error handling

### 4. **Hardcoded Node Configuration**
- `configs/node1/`, `configs/node2/`, `configs/node3/`
- Not scalable for different topologies
- Should be generated dynamically

### 5. **Entry Point Confusion**
- Multiple entry points: `e2e_ctl.sh`, `build.sh`, `start-network.sh` (legacy)
- No single unified CLI
- Inconsistent command naming

### 6. **Documentation Outdated**
- QEVM-focused instead of generic cellframe-node
- Mixed instructions (legacy + new)
- No clear migration path

## 🎯 Refactoring Goals

### Primary Goals
1. ✅ Remove ALL QEVM references → generic cellframe-node
2. ✅ Consolidate temporary files into `cache/`
3. ✅ Migrate bash scripts to Python modules
4. ✅ Create unified `stage_env.py` CLI
5. ✅ Dynamic configuration generation
6. ✅ Update documentation

### Success Criteria
- ✅ 0 QEVM references (except git history)
- ✅ All bash scripts replaced with Python
- ✅ Single entry point: `stage_env.py`
- ✅ Clean directory structure
- ✅ All tests passing
- ✅ Comprehensive documentation

## 📋 Next Steps

1. ✅ **Phase 14.5.1.2:** Remove QEVM specificity
   - Search & replace QEVM references
   - Rename configs
   - Update documentation

2. ✅ **Phase 14.5.1.3:** Reorganize directories
   - Move temporary files to `cache/`
   - Create `config/`, `src/` structure
   - Update `.gitignore`

3. ✅ **Phase 14.5.1.4:** Migrate bash to Python
   - Convert 15 scripts to Python modules
   - Add type hints and docstrings
   - Create unit tests

4. ✅ **Phase 14.5.1.5:** Create `stage_env.py`
   - Unified CLI with click
   - Commands: start, stop, status, build, clean, run-tests
   - Integration with Python modules

5. ✅ **Phase 14.5.1.6:** Create `tests/run.sh`
   - Unified test runner
   - venv management
   - Test aggregation

6. ✅ **Phase 14.5.1.7:** Update documentation
   - Remove QEVM references
   - Document new structure
   - Migration guide

7. ✅ **Phase 14.5.1.8:** Validation
   - Build and run tests
   - Verify all functionality
   - CI/CD integration

## 📝 Notes

- Current infrastructure is QEVM-specific, not suitable for generic cellframe-node testing
- Major refactoring required to make it production-ready
- Estimated effort: 2-3 weeks for full implementation
- High complexity due to bash-to-Python migration and architectural changes

