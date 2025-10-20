# Stage Environment Refactoring Plan

**Task:** Phase 14.5.1 - Рефакторинг E2E тестовой инфраструктуры  
**Date:** 2025-10-19  
**Priority:** CRITICAL  
**Estimated Duration:** 2-3 weeks  

## 🎯 Overall Goals

Transform tests/stage-env from QEVM-specific infrastructure into generic, maintainable, Python-based cellframe-node testing environment.

### Success Criteria
- ✅ 0 QEVM references (except git history)
- ✅ All bash scripts replaced with Python modules
- ✅ Single unified entry point: `stage_env.py`
- ✅ Clean directory structure with proper separation
- ✅ All tests passing after migration
- ✅ Comprehensive documentation

## 📋 Phase Breakdown

### Phase 14.5.1.1: Analysis & Documentation ✅ IN PROGRESS
**Duration:** 1 day  
**Status:** 90% complete

#### Tasks
- [x] Analyze current structure
- [x] Count QEVM references (278 found)
- [x] Create dependency graph
- [x] Document current workflows
- [ ] Create detailed migration checklist

#### Deliverables
- ✅ `docs/stage_env_refactoring/current_structure.md`
- ✅ `docs/stage_env_refactoring/dependencies.dot`
- 🔄 `docs/stage_env_refactoring/migration_plan.md` (this file)

---

### Phase 14.5.1.2: Remove QEVM Specificity
**Duration:** 2-3 days  
**Priority:** HIGH  
**Dependencies:** 14.5.1.1

#### Search & Replace Strategy

| Old Term | New Term | Context |
|----------|----------|---------|
| `qevm-stagenet` | `test-network` | Generic test network name |
| `QEVM` | `Cellframe Node` | General references |
| `qevm` | `cellframe` | Variable names |
| `QEVM Plugin` | `Test Environment` | Documentation |
| `qevm-node` | `cf-node` | Service names |
| `qevm.master` | `test-network.master` | Certificate prefixes |

#### Files to Modify

**Configuration Files** (Priority: CRITICAL)
- [ ] `configs/templates/qevm-plugin.cfg` → DELETE or genericize
- [ ] `configs/templates/qevm-stagenet.cfg` → `test-network.cfg`
- [ ] `configs/templates/cellframe-node.cfg.d/enable-qevm-stagenet.cfg` → `enable-test-network.cfg`
- [ ] `network-topology.json` → update `network.name`

**Docker Files** (Priority: HIGH)
- [ ] `docker-compose.yml`
  - Service names: `qevm-node-*` → `cf-node-*`
  - Network name: `qevm-testnet` → `cf-testnet`
  - Environment variables: `QEVM_*` → `CF_*`
  - Remove QEVM comments
- [ ] `Dockerfile.builder`
  - Remove QEVM-specific build steps
  - Genericize build paths
- [ ] `Dockerfile.cellframe`
  - Remove QEVM plugin copying
  - Genericize installation steps

**Documentation** (Priority: HIGH)
- [ ] `README.md`
  - Replace 50+ QEVM references
  - Update architecture diagrams
  - Update quick start guide
- [ ] `QUICK_START.md`
  - Replace 30+ QEVM references
  - Update example commands

**Python Tests** (Priority: MEDIUM)
- [ ] `tests/basic-connectivity.py` - update terminology
- [ ] `tests/consensus-test.py` - update terminology
- [ ] `tests/load-test.py` - update terminology
- [ ] `tests/requirements.txt` - verify dependencies

**Bash Scripts** (Priority: MEDIUM - will be replaced later)
- [ ] Update QEVM references in comments
- [ ] Update variable names
- [ ] Update log messages

#### Validation
```bash
# After changes, verify:
grep -r -i "qevm" --exclude-dir=.git --exclude-dir=cache | wc -l
# Should be 0
```

---

### Phase 14.5.1.3: Directory Reorganization
**Duration:** 1-2 days  
**Priority:** CRITICAL  
**Dependencies:** 14.5.1.2

#### Target Structure

```
tests/stage-env/
├── cache/                      # ✅ ALL temporary/generated files
│   ├── configs/               # Generated node configs
│   ├── data/                  # Node databases
│   ├── logs/                  # Node logs
│   ├── certs/                 # Generated certificates
│   ├── monitoring/            # Metrics and monitoring data
│   ├── results/               # Test results
│   └── crash-artifacts/       # Core dumps and crash reports
├── config/                     # ✅ Versioned configurations
│   ├── topologies/
│   │   ├── default.json       # Basic topology
│   │   ├── minimal.json       # 1 root + 1 master
│   │   └── full.json          # Full test network
│   ├── templates/             # Config templates
│   │   ├── cellframe-node.cfg.template
│   │   ├── test-network.cfg
│   │   └── chains/
│   │       └── main.cfg
│   └── stage_env_config.yaml  # Main config
├── src/                        # ✅ Python source code
│   ├── __init__.py
│   ├── network/
│   │   ├── __init__.py
│   │   ├── manager.py         # NetworkManager class
│   │   ├── node.py            # Node abstraction
│   │   └── topology.py        # Topology loader
│   ├── build/
│   │   ├── __init__.py
│   │   └── builder.py         # BuildManager class
│   ├── certs/
│   │   ├── __init__.py
│   │   ├── generator.py       # CertGenerator (Python wrapper)
│   │   ├── cert_generator.c   # C utility
│   │   └── CMakeLists.txt
│   ├── config/
│   │   ├── __init__.py
│   │   ├── loader.py          # Config loader
│   │   └── validator.py       # Config validation
│   ├── docker/
│   │   ├── __init__.py
│   │   ├── compose.py         # Docker Compose wrapper
│   │   ├── entrypoint.py      # Entry point logic
│   │   └── init_node.py       # Node initialization
│   ├── monitoring/
│   │   ├── __init__.py
│   │   ├── health.py          # Health checker
│   │   ├── supervisor.py      # Node supervisor
│   │   └── crash_handler.py   # Crash handler
│   └── utils/
│       ├── __init__.py
│       ├── logger.py          # Logging setup
│       └── cli.py             # CLI helpers
├── tests/functional/           # ✅ Moved from tests/
│   ├── __init__.py
│   ├── test_basic_connectivity.py
│   ├── test_consensus.py
│   ├── test_token_operations.py
│   └── requirements.txt
├── stage_env.py                # ✅ Main CLI entry point
├── docker-compose.yml          # ⚠️ Updated
├── Dockerfile.*                # ⚠️ Updated
├── requirements.txt            # ✅ Python dependencies
├── .gitignore                  # ✅ Updated
├── README.md                   # ⚠️ Updated
└── QUICK_START.md              # ⚠️ Updated
```

#### Migration Steps

1. **Create new structure**
   ```bash
   mkdir -p {cache/{configs,data,logs,certs,monitoring,results,crash-artifacts},config/topologies,config/templates/chains,src/{network,build,certs,config,docker,monitoring,utils},tests/functional}
   touch src/__init__.py src/*/__init__.py tests/functional/__init__.py
   ```

2. **Move existing files**
   ```bash
   # Use git mv to preserve history
   git mv certs cache/certs
   git mv logs cache/logs
   git mv data cache/data
   git mv monitoring cache/monitoring
   git mv results cache/results
   git mv tools/cert-generator.c src/certs/
   git mv tools/CMakeLists.txt src/certs/
   git mv network-topology.json config/topologies/default.json
   git mv tests/*.py tests/functional/
   git mv tests/requirements.txt tests/functional/
   ```

3. **Update .gitignore**
   ```
   # Temporary and generated files
   cache/
   !cache/.gitkeep
   
   # Python
   __pycache__/
   *.py[cod]
   *$py.class
   .pytest_cache/
   .coverage
   htmlcov/
   
   # Virtual environment
   venv/
   env/
   .venv/
   
   # IDE
   .vscode/
   .idea/
   *.swp
   *.swo
   ```

4. **Create .gitkeep files**
   ```bash
   touch cache/.gitkeep
   touch cache/{configs,data,logs,certs,monitoring,results,crash-artifacts}/.gitkeep
   ```

---

### Phase 14.5.1.4: Bash to Python Migration
**Duration:** 1 week  
**Priority:** CRITICAL  
**Dependencies:** 14.5.1.3

#### Migration Priority Order

1. **High Priority** (Core functionality)
   - `e2e_ctl.sh` → `stage_env.py` + `src/orchestrator.py`
   - `scripts/network-manager.sh` → `src/network/manager.py`
   - `scripts/build-manager.sh` → `src/build/builder.py`

2. **Medium Priority** (Support functionality)
   - `generate-all-certs.sh` → `src/certs/generator.py`
   - `scripts/init-node.sh` → `src/docker/init_node.py`
   - `scripts/docker-entrypoint.sh` → `src/docker/entrypoint.py`

3. **Low Priority** (Utilities)
   - `scripts/node-supervisor.sh` → `src/monitoring/supervisor.py`
   - `scripts/health-check.sh` → `src/monitoring/health.py`
   - `scripts/crash-handler.sh` → `src/monitoring/crash_handler.py`
   - `check-network.sh` → `src/network/checker.py`
   - `build.sh` → `src/build/build_cli.py`
   - `build-and-package.sh` → `src/build/packager.py`
   - `scripts/update-validator-addrs.sh` → `src/certs/updater.py`
   - `generate-validator-certs.sh` → integrated into `src/certs/generator.py`

#### Python Requirements

Create `requirements.txt`:
```txt
# CLI Framework
click>=8.0.0          # CLI framework
rich>=13.0.0          # Terminal formatting and progress bars

# Configuration
pyyaml>=6.0.0         # YAML parsing
jsonschema>=4.0.0     # JSON schema validation
jinja2>=3.0.0         # Template rendering

# Docker Integration
docker>=6.0.0         # Docker SDK for Python
docker-compose>=1.29  # Docker Compose Python wrapper

# System & Monitoring
psutil>=5.0.0         # Process and system monitoring
requests>=2.28.0      # HTTP requests for health checks

# Development & Testing
pytest>=7.0.0         # Testing framework
pytest-asyncio>=0.20  # Async testing
black>=22.0.0         # Code formatting
mypy>=0.990           # Type checking
pylint>=2.15.0        # Linting
```

#### Coding Standards

All Python code must follow:
- **Type hints** for all functions
- **Docstrings** (Google style)
- **Error handling** with proper logging
- **Unit tests** for all modules
- **English** comments and docstrings (DAP SDK standard)

Example:
```python
def build_artifacts(
    build_type: str = "debug",
    clean: bool = False,
    parallel: int = 4
) -> BuildResult:
    """
    Build cellframe-node artifacts.
    
    Args:
        build_type: Build type ('debug' or 'release')
        clean: Perform clean build
        parallel: Number of parallel jobs
        
    Returns:
        BuildResult containing status and artifacts
        
    Raises:
        BuildError: If build fails
    """
    logger.info(f"Building artifacts (type={build_type}, clean={clean})")
    # Implementation
    pass
```

---

### Phase 14.5.1.5: Create stage_env.py CLI
**Duration:** 2-3 days  
**Priority:** CRITICAL  
**Dependencies:** 14.5.1.4

#### CLI Structure

```python
# stage_env.py
import click
from src.orchestrator import StageEnvironment

@click.group()
@click.option('--config', '-c', default='config/stage_env_config.yaml')
@click.option('--topology', '-t', default='config/topologies/default.json')
@click.option('--verbose', '-v', is_flag=True)
@click.pass_context
def cli(ctx, config, topology, verbose):
    """Stage Environment CLI for cellframe-node testing."""
    ctx.obj = StageEnvironment(config, topology, verbose)

@cli.command()
@click.option('--rebuild', is_flag=True, help='Rebuild artifacts')
@click.option('--clean', is_flag=True, help='Clean build')
@click.option('--wait-ready', is_flag=True, default=True)
@click.pass_obj
def start(env, rebuild, clean, wait_ready):
    """Start the test environment."""
    if rebuild or not env.builder.artifacts_exist():
        env.builder.build(clean=clean)
    env.network.start()
    if wait_ready:
        env.network.wait_ready()

@cli.command()
@click.pass_obj
def stop(env):
    """Stop the test environment."""
    env.network.stop()

@cli.command()
@click.pass_obj
def status(env):
    """Show environment status."""
    status = env.network.status()
    # Display with rich

@cli.command()
@click.option('--clean', is_flag=True)
@click.option('--release', is_flag=True)
@click.pass_obj
def build(env, clean, release):
    """Build artifacts."""
    build_type = 'release' if release else 'debug'
    env.builder.build(clean=clean, build_type=build_type)

@cli.command()
@click.pass_obj
def clean(env):
    """Clean cache and artifacts."""
    env.clean_cache()

@cli.command()
@click.argument('test_dirs', nargs=-1)
@click.option('--e2e', is_flag=True)
@click.option('--functional', is_flag=True)
@click.option('--all', 'run_all', is_flag=True)
@click.option('--filter', '-k', help='Filter tests by name')
@click.option('--parallel', '-n', type=int, default=1)
@click.pass_obj
def run_tests(env, test_dirs, e2e, functional, run_all, filter, parallel):
    """Run tests."""
    results = env.test_runner.run(
        test_dirs=test_dirs,
        e2e=e2e,
        functional=functional,
        run_all=run_all,
        filter_pattern=filter,
        parallel=parallel
    )
    # Display results

@cli.command()
@click.argument('node_name')
@click.pass_obj
def logs(env, node_name):
    """Show node logs."""
    env.network.show_logs(node_name)

@cli.command()
@click.argument('node_name')
@click.pass_obj
def shell(env, node_name):
    """Open shell in node container."""
    env.network.exec_shell(node_name)

if __name__ == '__main__':
    cli()
```

---

### Phase 14.5.1.6: Create tests/run.sh
**Duration:** 1 day  
**Priority:** MEDIUM  
**Dependencies:** 14.5.1.5

#### Script Structure

```bash
#!/bin/bash
# tests/run.sh - Unified test runner for cellframe-node

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
STAGE_ENV_DIR="$PROJECT_ROOT/tests/stage-env"
VENV_DIR="$PROJECT_ROOT/tests/.venv"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

# Parse arguments
CLEAN=false
E2E=false
FUNCTIONAL=false
NO_VENV=false
FILTER=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --clean) CLEAN=true; shift ;;
        --e2e) E2E=true; shift ;;
        --functional) FUNCTIONAL=true; shift ;;
        --no-venv) NO_VENV=true; shift ;;
        --filter) FILTER="$2"; shift 2 ;;
        *) log_error "Unknown option: $1"; exit 1 ;;
    esac
done

# Setup venv
if [ "$NO_VENV" = false ]; then
    if [ ! -d "$VENV_DIR" ]; then
        log_info "Creating virtual environment..."
        python3 -m venv "$VENV_DIR"
    fi
    
    log_info "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
    
    log_info "Installing dependencies..."
    pip install -q --upgrade pip
    pip install -q -r "$STAGE_ENV_DIR/requirements.txt"
    pip install -q -r "$STAGE_ENV_DIR/tests/functional/requirements.txt"
fi

# Clean if requested
if [ "$CLEAN" = true ]; then
    log_info "Cleaning environment..."
    cd "$STAGE_ENV_DIR"
    python3 stage_env.py clean
fi

# Start environment
log_info "Starting stage environment..."
cd "$STAGE_ENV_DIR"
python3 stage_env.py start --wait-ready

# Run tests
TEST_ARGS=""
[ "$E2E" = true ] && TEST_ARGS="$TEST_ARGS --e2e"
[ "$FUNCTIONAL" = true ] && TEST_ARGS="$TEST_ARGS --functional"
[ -n "$FILTER" ] && TEST_ARGS="$TEST_ARGS --filter $FILTER"

if [ -z "$TEST_ARGS" ]; then
    TEST_ARGS="--all"
fi

log_info "Running tests: $TEST_ARGS"
python3 stage_env.py run-tests $TEST_ARGS

# Capture exit code
TEST_EXIT_CODE=$?

# Cleanup
log_info "Stopping stage environment..."
python3 stage_env.py stop

# Report results
if [ $TEST_EXIT_CODE -eq 0 ]; then
    log_info "✅ All tests passed!"
else
    log_error "❌ Tests failed with exit code $TEST_EXIT_CODE"
fi

exit $TEST_EXIT_CODE
```

---

### Phase 14.5.1.7: Update Documentation
**Duration:** 2 days  
**Priority:** HIGH  
**Dependencies:** 14.5.1.6

#### Documents to Create/Update

1. **README.md** - Main documentation
   - Remove all QEVM references
   - Document new structure
   - Update quick start guide
   - Add architecture overview

2. **QUICK_START.md** - Quick start guide
   - Simple examples
   - Common use cases
   - Troubleshooting

3. **docs/stage_env_architecture.md** - Architecture
   - System design
   - Component interaction
   - Data flow

4. **docs/stage_env_cli.md** - CLI documentation
   - Command reference
   - Options and flags
   - Examples

5. **docs/testing_guide.md** - Testing guide
   - How to write tests
   - Test organization
   - Best practices

6. **docs/stage_env_refactoring.md** - Refactoring history
   - What changed
   - Why it changed
   - Migration guide for users

---

### Phase 14.5.1.8: Validation
**Duration:** 2-3 days  
**Priority:** CRITICAL  
**Dependencies:** All previous phases

#### Validation Checklist

**1. Build Validation**
- [ ] Clean build succeeds: `./stage_env.py build --clean`
- [ ] Debug build works
- [ ] Release build works
- [ ] Incremental build works

**2. Environment Validation**
- [ ] Start environment: `./stage_env.py start`
- [ ] Check status: `./stage_env.py status`
- [ ] View logs: `./stage_env.py logs node1`
- [ ] Stop environment: `./stage_env.py stop`

**3. Test Validation**
- [ ] E2E tests pass: `./tests/run.sh --e2e`
- [ ] Functional tests pass: `./tests/run.sh --functional`
- [ ] All tests pass: `./tests/run.sh`
- [ ] Test filtering works: `./tests/run.sh --filter connectivity`

**4. QEVM Removal Validation**
- [ ] No QEVM references in code: `grep -r "qevm" --exclude-dir=.git | wc -l` → 0
- [ ] No QEVM in logs
- [ ] No QEVM in generated configs

**5. Python Quality Validation**
- [ ] Type checking: `mypy src/`
- [ ] Linting: `pylint src/`
- [ ] Formatting: `black --check src/`
- [ ] Unit tests: `pytest src/`

**6. Documentation Validation**
- [ ] README.md is up-to-date
- [ ] QUICK_START.md works
- [ ] All commands in docs are correct
- [ ] No broken links

**7. CI/CD Integration**
- [ ] Tests run in CI
- [ ] Build artifacts are created
- [ ] Test reports are generated

---

## 📊 Progress Tracking

### Overall Progress: 10%

| Phase | Status | Progress | Notes |
|-------|--------|----------|-------|
| 14.5.1.1 | 🔄 IN PROGRESS | 90% | Documentation almost complete |
| 14.5.1.2 | ⏳ PENDING | 0% | Ready to start |
| 14.5.1.3 | ⏳ PENDING | 0% | Depends on 14.5.1.2 |
| 14.5.1.4 | ⏳ PENDING | 0% | Major effort, 1 week |
| 14.5.1.5 | ⏳ PENDING | 0% | Depends on 14.5.1.4 |
| 14.5.1.6 | ⏳ PENDING | 0% | Quick task |
| 14.5.1.7 | ⏳ PENDING | 0% | Documentation updates |
| 14.5.1.8 | ⏳ PENDING | 0% | Final validation |

---

## 🎯 Next Immediate Actions

1. ✅ Complete Phase 14.5.1.1 documentation
2. 🔄 Begin Phase 14.5.1.2: Start QEVM removal
   - Create search & replace script
   - Update configuration files
   - Update Docker files
3. 📋 Prepare for Phase 14.5.1.3: Directory reorganization
   - Create migration script
   - Test with git mv

---

## 📝 Notes & Considerations

### Technical Debt
- Bash scripts total ~2000 lines of code
- Complex state management in bash
- Limited error handling
- No type safety

### Risks
- Breaking existing workflows during migration
- Docker Compose compatibility
- Certificate generation might fail
- Tests might break after restructuring

### Mitigation
- Incremental migration with validation at each step
- Keep bash scripts until Python equivalents are tested
- Comprehensive testing before cleanup
- Document all breaking changes

---

## 🔗 References

- Task File: `.context/tasks/cf20_token_utxo_blocking_mechanism.json`
- Current Structure: `docs/stage_env_refactoring/current_structure.md`
- Dependencies Graph: `docs/stage_env_refactoring/dependencies.dot`
- DAP SDK Standards: `.context/modules/standards/dap_sdk_coding_standards.json`

