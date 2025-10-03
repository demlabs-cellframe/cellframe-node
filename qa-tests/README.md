# Cellframe Node QA Testing

Automated testing suite for Cellframe Node on Linux.

## Overview

This directory contains automated tests for validating Cellframe Node installation and functionality according to the QA specification document (`QA_SPECIFICATION_LINUX.md`).

## Files

- `Dockerfile.qa` - Docker container for isolated testing environment
- `test-suite.sh` - Complete test suite script
- `health-check.sh` - Quick health check script (for monitoring)
- `README.md` - This file

## Requirements

- Docker installed
- At least 5GB free disk space
- Internet connection (for package installation)

## Usage

### Running Tests in Docker

Build the test container:
```bash
docker build -f Dockerfile.qa -t cellframe-node-qa .
```

Run the test suite:
```bash
docker run --rm --privileged cellframe-node-qa
```

Run with systemd support (recommended):
```bash
docker run --rm --privileged \
  --tmpfs /run \
  --tmpfs /run/lock \
  -v /sys/fs/cgroup:/sys/fs/cgroup:ro \
  cellframe-node-qa
```

### Running Tests Locally

You can also run the test suite directly on a Linux system:

```bash
sudo ./test-suite.sh
```

**Warning**: This will install cellframe-node on your system.

### Health Check Only

To run just the health check (requires cellframe-node already installed):

```bash
sudo ./health-check.sh
```

## Test Sections

The test suite includes the following sections:

1. **Pre-Installation Checks**
   - Disk space verification
   - Internet connectivity
   - No existing processes

2. **Package Installation**
   - Repository configuration
   - Package installation
   - Exit code verification

3. **File System Verification**
   - Directory structure
   - Executable files
   - Configuration files

4. **Python Environment**
   - Python interpreter
   - Pip package manager
   - Required packages (pycfhelpers, pycftools)

5. **Service Management**
   - Systemd service status
   - Process running
   - Auto-start configuration

6. **CLI Functionality**
   - Basic CLI commands
   - Response time
   - Network queries

7. **Network Connectivity**
   - Backbone network status
   - KelVPN network status
   - Node connections

8. **Wallet Functionality**
   - Wallet creation
   - Wallet queries

9. **Resource Usage**
   - Memory consumption
   - CPU usage

10. **Log Analysis**
    - Error detection
    - Log integrity

11. **Configuration Verification**
    - Config file validation
    - Network configuration

## Exit Codes

- `0` - All tests passed
- `1` - One or more tests failed

## Output Format

The test suite provides colored output:
- 🟢 **[PASS]** - Test passed
- 🔴 **[FAIL]** - Test failed (with error details)
- 🟡 **[WARN]** - Warning (non-critical)
- 🔵 **[INFO]** - Informational message

Example output:
```
===========================================================
  1. Pre-Installation Checks
===========================================================

[PASS] Disk space sufficient (>5GB available)
[PASS] Internet connectivity available
[PASS] No existing cellframe-node process running

...

===========================================================
  TEST RESULTS SUMMARY
===========================================================

Total tests:  45
Passed:       45
Failed:       0

✓ ALL TESTS PASSED
```

## Continuous Integration

### GitHub Actions

Add to `.github/workflows/qa-tests.yml`:

```yaml
name: QA Tests

on: [push, pull_request]

jobs:
  qa-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build QA container
        run: docker build -f qa-tests/Dockerfile.qa -t cellframe-node-qa .
      
      - name: Run tests
        run: |
          docker run --rm --privileged \
            --tmpfs /run \
            --tmpfs /run/lock \
            -v /sys/fs/cgroup:/sys/fs/cgroup:ro \
            cellframe-node-qa
```

### GitLab CI

Add to `.gitlab-ci.yml`:

```yaml
qa-tests:
  stage: test
  image: docker:latest
  services:
    - docker:dind
  script:
    - cd qa-tests
    - docker build -f Dockerfile.qa -t cellframe-node-qa .
    - docker run --rm --privileged cellframe-node-qa
  only:
    - merge_requests
    - master
```

## Monitoring

### Docker Health Check

The health check script is automatically run by Docker when using `HEALTHCHECK`:

```bash
docker run -d --name cellframe-node-test \
  --health-cmd="/opt/qa-tests/health-check.sh" \
  --health-interval=30s \
  --health-timeout=10s \
  --health-retries=3 \
  cellframe-node-qa
  
# Check health status
docker inspect --format='{{.State.Health.Status}}' cellframe-node-test
```

### Cron Job Monitoring

Schedule regular health checks:

```bash
# Add to crontab
*/5 * * * * /opt/qa-tests/health-check.sh || echo "Cellframe node unhealthy" | mail -s "Alert" admin@example.com
```

## Troubleshooting

### Tests Failing in Docker

1. **Systemd issues**: Make sure to run with `--privileged` and proper tmpfs mounts
2. **Network timeout**: Some tests wait for network sync; increase timeout if needed
3. **Resource limits**: Ensure Docker has at least 2GB RAM and 5GB disk

### Slow Tests

- First-time sync can take 15-30 minutes
- Adjust wait times in test-suite.sh if needed
- Use faster storage (SSD) for better performance

### Test Failures

Check the logs:
```bash
# Inside container
tail -100 /opt/cellframe-node/var/log/cellframe-node.log

# Service status
systemctl status cellframe-node
```

## Customization

### Adjusting Test Timeouts

Edit `test-suite.sh` and modify wait times:

```bash
# Network initialization wait
sleep 30  # Increase this if networks need more time

# CLI timeout
timeout 5  # Increase if CLI is slow to respond
```

### Adding Custom Tests

Add new test sections to `test-suite.sh`:

```bash
test_section "12. Custom Test Section"

if [[ condition ]]; then
    test_pass "Custom test description"
else
    test_fail "Custom test" "Error message"
fi
```

### Changing Test Networks

Modify debconf pre-configuration in `test-suite.sh`:

```bash
cellframe-node cellframe-node/backbone_enabled boolean false
cellframe-node cellframe-node/kelvpn_enabled boolean false
cellframe-node cellframe-node/riemann_enabled boolean true
```

## Reference Documentation

- Main QA Specification: `../QA_SPECIFICATION_LINUX.md`
- Cellframe Node Wiki: https://wiki.cellframe.net/
- Installation Guide: `../README.md`

## Support

For issues or questions:
- GitHub Issues: https://github.com/demlabs-cellframe/cellframe-node/issues
- Telegram: t.me/cellframe_dev_en

## License

Same as Cellframe Node project

