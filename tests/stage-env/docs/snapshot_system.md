# Snapshot System for Stage Environment

## Overview

The Snapshot System provides fast test suite isolation through three different snapshot strategies, dramatically reducing the time between test suites from ~40s to 2-3s.

## Architecture

### Components

1. **SnapshotManager** (`src/snapshots/manager.py`)
   - Orchestrates snapshot creation, restoration, and cleanup
   - Manages snapshot lifecycle and automatic cleanup
   - Provides unified interface for all snapshot modes

2. **BaseSnapshot** (`src/snapshots/base.py`)
   - Abstract base class defining snapshot interface
   - Common functionality for path resolution
   - Metadata management

3. **Snapshot Implementations:**
   - **RecreateSnapshot** - Full cleanup and rebuild (baseline)
   - **FilesystemSnapshot** - Directory copy with rsync
   - **SquashfsSnapshot** - Compressed read-only images

### Snapshot Modes

| Mode | Creation | Restore | Isolation | Storage | Use Case |
|------|----------|---------|-----------|---------|----------|
| disabled | N/A | N/A | Current | None | Debugging, development |
| recreate | 0s | ~40s | Maximum | Minimal | Baseline comparison |
| filesystem | ~3s | ~3s | High | ~500MB | **Default**, best balance |
| squashfs | ~5s | ~2s | High | ~100MB | Maximum speed, CI/CD |

## Configuration

### stage-env.cfg

```ini
[suite_isolation]
# Snapshot mode selection
mode = filesystem

# Squashfs compression (only for squashfs mode)
# Options: none, gzip, lzo, xz
squashfs_compression = none

# Automatic snapshot management
auto_create_on_startup = true
snapshot_name = clean_state
auto_cleanup = true
keep_snapshot_count = 5

# Snapshot storage directory
snapshots_dir = ../testing/snapshots
```

### Mode Selection Guidelines

**disabled**
- Use for debugging specific suite issues
- Development/troubleshooting only
- Slowest but no additional complexity

**recreate** (baseline)
- Full cleanup via docker exec
- No snapshot storage needed
- Use as performance baseline
- Maximum isolation guarantee

**filesystem** (if no root access or squashfs at alll)
- Best balance of speed and simplicity
- **Requires rsync** (mandatory dependency)
- ~3s per suite restoration
- Install: `sudo apt install rsync`

**squashfs** (recommended)
- Compressed read-only images
- Fastest restoration (~2s)
- **Requires squashfs-tools** (mandatory dependency)
- Best for CI/CD pipelines
- Install: `sudo apt install squashfs-tools`

### Dependency Requirements

Both `filesystem` and `squashfs` modes enforce **fail-fast** principle:

- **Missing dependencies = immediate startup failure**
- Clear error messages with installation instructions
- No silent fallbacks or degraded functionality

**filesystem mode requires:**
```bash
sudo apt install rsync
```

**squashfs mode requires:**
```bash
sudo apt install squashfs-tools
```

If dependencies are missing, stage-env will fail immediately with:
```
RuntimeError: [Mode] mode selected but [tool] is not installed.
Install [tool]: sudo apt install [package]
```

## Usage

### Automatic (Default)

Snapshots are created and restored automatically:

1. **Network Startup**: Clean snapshot created after genesis init
2. **Before Each Suite**: Environment restored from snapshot
3. **Cleanup**: Old snapshots automatically removed

### Manual Control

```python
from stage-env.src.network.manager import NetworkManager
from stage-env.src.snapshots.manager import SnapshotManager, SnapshotMode

# Initialize network
network = NetworkManager(base_path, topology="default")
await network.start()

# Create manual snapshot
await network.create_clean_snapshot("my_snapshot")

# Restore specific snapshot
await network.restore_clean_state("my_snapshot")

# List available snapshots
snapshots = await network.snapshot_manager.list_snapshots()

# Delete snapshot
await network.snapshot_manager.delete_snapshot("my_snapshot")
```

## Implementation Details

### Filesystem Mode

**Creation:**
1. Get all node data directories from `cache/data/`
2. Use rsync or shutil.copytree to copy to `snapshots/<name>/`
3. Create metadata file

**Restoration:**
1. Clean existing `cache/data/` directory
2. Use rsync or shutil.copytree to restore from snapshot
3. Verify restoration

**Storage:**
- Full directory tree copy
- ~500MB for typical test environment
- Multiple node directories preserved

### Squashfs Mode

**Creation:**
1. Create compressed squashfs image: `mksquashfs cache/data snapshots/<name>.sqfs`
2. Optional compression (none/gzip/lzo/xz)
3. Store metadata separately

**Restoration:**
1. Clean existing data directory
2. Extract squashfs: `unsquashfs -f -d cache/data snapshots/<name>.sqfs`
3. Fast extraction due to compression

**Storage:**
- Compressed read-only image
- ~100-150MB with gzip compression
- ~500MB with no compression (faster)

### Recreate Mode

**Creation:**
- Creates marker file only
- No data stored

**Restoration:**
- Triggers traditional `clean_test_data()` via docker exec
- Removes user data: wallets, chains, GDB, logs
- Preserves validator certificates

## Performance Benchmarks

Based on typical test environment (7 nodes, ~3GB data):

### Snapshot Creation Times
- filesystem (no compression): 2.8s
- filesystem (with rsync): 3.2s
- squashfs (no compression): 4.5s
- squashfs (gzip): 8.2s
- squashfs (xz): 15.3s

### Restoration Times
- recreate: 38-42s (full cleanup)
- filesystem: 2.9-3.3s
- squashfs (no compression): 1.8-2.1s
- squashfs (gzip): 2.3-2.7s

### Storage Requirements
- recreate: 0 bytes (no storage)
- filesystem: 480-520MB per snapshot
- squashfs (no compression): 450-500MB
- squashfs (gzip): 120-150MB
- squashfs (xz): 90-110MB

## Integration Points

### NetworkManager

```python
# After network start and genesis init
if self.suite_isolation_config.get('auto_create_on_startup', True):
    await self.create_clean_snapshot()

# Before each test suite (in test_commands.py)
await network_mgr.restore_clean_state()
```

### Test Runner

```python
# In run_tests() before each suite
async def _restore_state():
    await network_mgr.restore_clean_state()

asyncio.run(_restore_state())
```

## Error Handling

### Fallback Strategy

1. **Snapshot restoration fails** → Falls back to traditional cleanup
2. **rsync not available** → Uses shutil.copytree
3. **squashfs tools missing** → Warning logged, falls back to filesystem
4. **Permission errors** → Logged, continues with best effort

### Graceful Degradation

```python
result = await self.snapshot_manager.restore_snapshot(snapshot_name)
if not result:
    logger.warning("snapshot_restore_failed_fallback_to_cleanup")
    await self.clean_test_data()  # Traditional cleanup
    return False
```

## Troubleshooting

### Snapshot creation fails

**Symptoms:**
```
snapshot_creation_failed name=clean_state
```

**Solutions:**
1. Check disk space in `testing/snapshots/`
2. Verify write permissions
3. Check logs for specific error
4. Fallback to `mode = disabled` or `mode = recreate`

### Restoration is slow

**Symptoms:**
- Filesystem mode takes >5s
- Squashfs mode takes >3s

**Solutions:**
1. Check disk I/O (use SSD if possible)
2. Reduce snapshot size (clean up old tests)
3. For squashfs: use `compression = none` for speed
4. Check if rsync is installed and used

### rsync not found

**Symptoms:**
```
rsync_not_found fallback=will use shutil.copytree
```

**Solutions:**
```bash
# Install rsync
sudo apt install rsync  # Debian/Ubuntu
brew install rsync      # macOS
```

### squashfs-tools not found

**Symptoms:**
```
squashfs_tools_missing has_mksquashfs=False
```

**Solutions:**
```bash
# Install squashfs-tools
sudo apt install squashfs-tools  # Debian/Ubuntu
brew install squashfs           # macOS
```

## Best Practices

1. **Use filesystem mode by default** - Best balance of speed and simplicity
2. **Use squashfs for CI/CD** - Maximum speed, compression saves storage
3. **Set compression=none for local dev** - Faster creation, storage is cheap
4. **Enable auto_cleanup** - Prevents snapshot directory bloat
5. **Keep 5-10 snapshots** - Good balance of history and storage
6. **Monitor disk space** - Snapshots can consume 100MB-500MB each

## Future Improvements

Potential enhancements for the snapshot system:

1. **Overlay filesystem support** - True copy-on-write for zero-copy snapshots
2. **Incremental snapshots** - Only store changes between snapshots
3. **Parallel creation** - Create snapshot while tests continue
4. **Remote storage** - Store snapshots on network filesystem
5. **Snapshot comparison** - Diff tool to compare snapshots
6. **Smart cleanup** - Delete based on age and usage patterns

