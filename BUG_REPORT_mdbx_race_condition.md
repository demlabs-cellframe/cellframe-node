# 🐛 Bug Report: MDBX Race Condition - Assertion Failure in dbi_update

**Date**: 2026-01-28  
**Severity**: CRITICAL (causes segfault)  
**Component**: `dap-sdk/global-db/dap_global_db_mdbx.c`

## 📋 Summary

MDBX assertion failure occurs when Global DB synchronization creates new database contexts while a CLI command attempts concurrent database access.

## 💥 Error Message

```
cellframe-node: mdbx:18610: dbi_update: Assertion `!env->dbs_flags[i] && !env->kvs[i].name.iov_len && !env->kvs[i].name.iov_base' failed.
Exit code: 139 (SIGSEGV - Segmentation Fault)
```

## 🔍 Root Cause

**Race condition** in MDBX DBI (Database Instance) allocation:

1. **Thread 1**: Global DB sync creates DB context: `DB context for the group 'local.nodes.heated.0x0000000000001234' has been created`
2. **Thread 2**: CLI command `srv_stake order create` tries to access database
3. **Collision**: Both threads try to allocate/update same DBI slot simultaneously
4. **Assertion fails**: `dbi_update()` detects DBI slot is not empty but inconsistent

## 📍 Location

**File**: `dap-sdk/global-db/dap_global_db_mdbx.c`  
**Function**: `dbi_update()` around line 18610 in libmdbx

**Assertion**:
```c
assert(!env->dbs_flags[i] && !env->kvs[i].name.iov_len && !env->kvs[i].name.iov_base);
```

This assertion checks that DBI slot `i` is completely empty before allocation.

## 🔬 Reproduction Steps

1. Start cellframe-node with clean state
2. Node connects to network and begins Global DB sync
3. During sync (while DB contexts are being created), execute CLI command that accesses database:
   ```bash
   cellframe-node-cli srv_stake order create -net stagenet -value 0.05e+18 -cert stagenet.master.pvt.0
   ```
4. **Result**: Node crashes with assertion failure

**Timing**: Occurs ~5 seconds after node becomes ONLINE during initial Global DB sync.

## 📊 Log Evidence

```
[01/28/26-15:00:04] [ * ] [dap_global_db_mdbx] DB context for the group 'local.nodes.heated.0x0000000000001234' has been created
[01/28/26-15:00:04] [DBG] [dap_chain_node] dap_chain_node_mempool_process_all: Found 0 datums in mempool
cellframe-node: mdbx:18610: dbi_update: Assertion `!env->dbs_flags[i] && !env->kvs[i].name.iov_len && !env->kvs[i].name.iov_base' failed.
```

**Container**: `cellframe-stage-node-5`  
**Exit Code**: 139 (SIGSEGV)

## 🛠️ Workaround

Add delay after node restart to allow Global DB sync to complete:

```yaml
- docker_op: restart
  services: "{{_active_nodes}}"

- wait_network: online
  nodes: "{{_active_nodes}}"
  timeout: 60

- wait: "40s"  # Original wait

# CRITICAL: Additional wait for Global DB sync
- wait: "20s"  # Prevents race condition

# Now safe to execute DB operations
- cli: "srv_stake order create ..."
```

**Total wait**: 60s after restart ensures Global DB sync completes before DB access.

## ✅ Proper Fix (Recommendations)

### Option 1: Mutex Protection
Add mutex around DBI allocation in `dap_global_db_mdbx.c`:

```c
static pthread_mutex_t s_dbi_alloc_mutex = PTHREAD_MUTEX_INITIALIZER;

int dbi_update(...) {
    pthread_mutex_lock(&s_dbi_alloc_mutex);
    
    // Find free DBI slot
    for (int i = 0; i < env->dbs_count; i++) {
        if (!env->dbs_flags[i] && !env->kvs[i].name.iov_len) {
            // Allocate DBI
            env->dbs_flags[i] = ...;
            env->kvs[i].name = ...;
            break;
        }
    }
    
    pthread_mutex_unlock(&s_dbi_alloc_mutex);
}
```

### Option 2: Atomic Operations
Use C11 atomics for DBI slot allocation:

```c
#include <stdatomic.h>

atomic_bool dbi_slots[MAX_DBI_COUNT];

// Atomic compare-and-swap for DBI allocation
int allocate_dbi_slot() {
    for (int i = 0; i < MAX_DBI_COUNT; i++) {
        bool expected = false;
        if (atomic_compare_exchange_strong(&dbi_slots[i], &expected, true)) {
            return i;  // Successfully allocated
        }
    }
    return -1;  // No free slots
}
```

### Option 3: DBI Pool Pre-allocation
Pre-allocate DBI slots at startup to avoid runtime allocation races.

## 🎯 Impact

- **Severity**: Critical - causes node crash
- **Frequency**: Reproducible when DB operations occur during Global DB sync
- **Affected**: All nodes during network join/sync
- **Workaround**: Requires timing delays (not production-ready)

## 📝 Related Files

- `dap-sdk/global-db/dap_global_db_mdbx.c` - MDBX wrapper with race condition
- `tests/stage-env/scenarios/genesis/phase1_zerochain.yml` - Reproduction scenario
- `.context/tasks/mdbx_race_condition_investigation.json` - Investigation task

## 🔗 References

- MDBX documentation: https://erthink.github.io/libmdbx/
- Thread-safety considerations: DBI handles are NOT thread-safe by default
- Similar issues: Other projects hit this with concurrent MDBX DBI access

---

**Assigned to**: SDK Team  
**Priority**: P0 (Critical - causes crashes)  
**Target**: Next SDK release
