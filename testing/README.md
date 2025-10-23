# Testing Directory

This directory contains test artifacts and cache for Cellframe Node E2E testing.

## Structure

```
testing/
├── cache/              # Test environment cache
│   ├── certs/         # Generated certificates
│   ├── configs/       # Node configurations
│   ├── data/          # Node data (GDB, chains, wallets)
│   └── build/         # Build artifacts
│
└── artifacts/         # Test run artifacts
    └── run_YYYYMMDD_HHMMSS/    # Per-run directory
        ├── stage-env-logs/      # Stage environment logs
        ├── node-logs/           # Docker container logs
        ├── core-dumps/          # Core dumps (if any)
        ├── stack-traces/        # Stack traces from core dumps
        ├── health-logs/         # Health check logs
        └── summary.json         # Run summary

## Configuration

Paths are configured in `tests/stage-env.cfg`:

```ini
[paths]
cache_dir = ../testing/cache
artifacts_dir = ../testing/artifacts

[artifacts]
collect_node_logs = true
collect_health_logs = true
collect_crash_dumps = true
retain_days = 30
```

## Usage

Artifacts are collected automatically after each test run when using:

```bash
cd tests
./run.sh --e2e
./run.sh --functional
```

## Cleanup

Old artifacts are automatically cleaned up after `retain_days` (default: 30 days).

Manual cleanup:
```bash
# Remove all cache
rm -rf testing/cache/*

# Remove all artifacts
rm -rf testing/artifacts/*
```

## Git Ignore

This directory is gitignored to prevent committing large test artifacts and cache files.
Only this README and .gitignore are tracked.

