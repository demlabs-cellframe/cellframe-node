# Per-Node Package Sources

## Overview

Stage-env supports specifying different cellframe-node package sources for individual nodes. This enables:

- **Version Compatibility Testing**: Test how different versions interact
- **Regression Testing**: Verify new code works with older versions
- **Migration Testing**: Test upgrade paths
- **Bisecting**: Find which commit introduced a bug
- **Performance Comparison**: Compare different builds side-by-side

## Configuration Levels

Package sources can be specified at three levels:

1. **Global** (`stage-env.cfg` - `[node_source]` section)
   - Default for all nodes
   
2. **Per-Node in YAML** (`network.nodes[].package`)
   - Overrides global for specific nodes in test scenarios
   
3. **Per-Node in Config** (topology YAML files)
   - For permanent topology definitions

## YAML Scenario Syntax

### Basic Example

```yaml
network:
  topology: default
  nodes:
    - name: node1
      role: root
      validator: true
      package:
        type: local
        local_path: ../build/cellframe-node-5.6-LOCALBUILD-dbg-amd64.deb
    
    - name: node2
      role: master
      package:
        type: url
        url: https://pub.cellframe.net/linux/cellframe-node/master/cellframe-node-5.6-master-amd64.deb
```

### Package Source Types

#### 1. URL Source

Download pre-built package from HTTP/HTTPS URL:

```yaml
package:
  type: url
  url: https://pub.cellframe.net/linux/cellframe-node/master/cellframe-node-5.6-master-amd64.deb
  checksum: sha256:abc123...  # Optional: verify integrity
```

#### 2. Local Source

Use local .deb file:

```yaml
package:
  type: local
  local_path: ../build/cellframe-node-5.6-LOCALBUILD-dbg-amd64.deb
```

Paths are resolved relative to `stage-env/` directory.

#### 3. Repository Source

Build from git source:

```yaml
package:
  type: repository
  git_url: https://gitlab.demlabs.net/cellframe/cellframe-node.git
  branch: dev                 # or use commit: abc123def
  build_type: Release         # Debug, Release, RelWithDebInfo
```

## Complete Example: Version Compatibility Test

See `tests/e2e/examples/test_version_compatibility.yml` for a full example.

This scenario demonstrates:
- Node 1: Current development build (local)
- Node 2: Latest stable (URL)
- Node 3: Specific older version (URL)
- Node 4: Custom commit (repository)

The test verifies:
- All versions can connect and form a network
- Cross-version transactions work
- Each node reports correct version

## Use Cases

### 1. Test Current vs Latest

```yaml
nodes:
  - name: dev_node
    role: root
    package:
      type: local
      local_path: ../build/cellframe-node-current.deb
  
  - name: stable_node
    role: master
    package:
      type: url
      url: https://pub.cellframe.net/.../latest.deb
```

### 2. Regression Testing

```yaml
nodes:
  # New version
  - name: v5_6
    package:
      type: local
      local_path: ../build/cellframe-node-5.6.deb
  
  # Previous version  
  - name: v5_5
    package:
      type: url
      url: https://pub.cellframe.net/.../cellframe-node-5.5.deb
```

### 3. Bisecting Bugs

```yaml
nodes:
  # Known good commit
  - name: good_commit
    package:
      type: repository
      git_url: https://gitlab.demlabs.net/cellframe/cellframe-node.git
      commit: abc123def
      build_type: Debug
  
  # Known bad commit
  - name: bad_commit
    package:
      type: repository
      git_url: https://gitlab.demlabs.net/cellframe/cellframe-node.git
      commit: def456ghi
      build_type: Debug
```

### 4. Performance Comparison

```yaml
nodes:
  # Debug build (with symbols)
  - name: debug_build
    package:
      type: local
      local_path: ../build/cellframe-node-dbg.deb
  
  # Release build (optimized)
  - name: release_build
    package:
      type: local
      local_path: ../build/cellframe-node-release.deb
```

## Additional Per-Node Options

### Custom Packages

Install additional packages on specific nodes:

```yaml
nodes:
  - name: node1
    custom_packages:
      - gdb
      - valgrind
      - perf-tools
```

### Custom Environment

Set node-specific environment variables:

```yaml
nodes:
  - name: node1
    custom_env:
      DAP_DEBUG: "2"
      CELLFRAME_LOG_LEVEL: "debug"
```

## Implementation Details

### Docker Build Process

Each node with a custom package source:

1. Gets its own Docker build context
2. Downloads/copies the specified package
3. Installs it during image build
4. Caches the package for future builds

### Build Cache

Packages are cached in `cache/cellframe-packages/` to avoid re-downloading.

Cache is keyed by:
- Source type and URL/path/commit
- Architecture
- Build type

### Network Formation

All nodes, regardless of version:
- Use the same network configuration (stagenet)
- Share the same genesis state
- Can communicate via P2P protocol

## Limitations

### Protocol Compatibility

- Major version changes may break P2P protocol
- Test within compatible version ranges
- Check Cellframe Node compatibility matrix

### Architecture

- All nodes must use same CPU architecture
- Cannot mix amd64 and arm64 in same network

### Build Time

- Repository sources require building from source
- May take 10-30 minutes depending on hardware
- Use local builds for faster iteration

## Best Practices

### 1. Cache Builds

Build packages once, reuse in tests:

```bash
# Build once
cd cellframe-node
dpkg-buildpackage -b

# Reference in all tests
package:
  type: local
  local_path: ../build/cellframe-node-X.Y-LOCALBUILD-dbg-amd64.deb
```

### 2. Test Matrix

Create test suites for version combinations:

```yaml
# Current + Latest
tests/compatibility/current_vs_latest.yml

# Current + N-1
tests/compatibility/current_vs_previous.yml

# All recent versions
tests/compatibility/multi_version.yml
```

### 3. Tag Scenarios

Use tags to organize compatibility tests:

```yaml
tags: [compatibility, v5.6, regression]
```

Run with:
```bash
./stage_env.py run tests/compatibility/ --filter v5.6
```

### 4. Document Expectations

Clearly state which versions should be compatible:

```yaml
description: |
  Test v5.6-dev compatibility with v5.5-stable.
  Expected: All operations work, P2P protocol compatible.
  If fails: Check P2P protocol changes between versions.
```

## Troubleshooting

### Package Not Found

```
ERROR: Failed to download package from URL
```

**Solution**: Verify URL is accessible, check network/firewall.

### Build Failure

```
ERROR: Repository build failed
```

**Solution**: Check git URL, branch/commit exists, build dependencies installed.

### Version Mismatch

```
WARNING: Node reports different version than expected
```

**Solution**: Clear Docker cache, rebuild images, check package installation.

### Connection Failures

```
ERROR: Nodes cannot connect to each other
```

**Solution**: Check P2P protocol compatibility, network configuration, firewall rules.

## See Also

- [Scenario Language Reference](./Glossary.md)
- [Network Topology](./Topology.md)
- [Version Compatibility Test Example](../../e2e/examples/test_version_compatibility.yml)

