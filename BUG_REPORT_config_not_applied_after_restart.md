# Bug Report: Configuration Not Applied After Docker Restart

## Issue
When `config:` step modifies chain configuration (e.g., `is_add_directly` in `zerochain.cfg`) followed by `docker_op: restart`, the new configuration is **NOT applied** to the running containers.

## Root Cause
1. `config:` step regenerates configuration files in host cache (`cache/configs/nodeN/network/stagenet/zerochain.cfg`)
2. `docker restart` command restarts the container **WITHOUT reloading the configuration**
3. Cellframe-node process loads config files **only at startup** 
4. The bind mount (`cache/configs/.../network -> /opt/cellframe-node/etc/network`) reflects changes immediately on the filesystem, but the running process doesn't re-read them

## Reproduction
```yaml
- config: "{{network_name}}/zerochain"
  nodes: "{{seed_nodes}}"
  set:
    is_add_directly: "true"

- docker_op: restart  # <-- This does NOT apply the new config!
  services: "{{_active_nodes}}"
```

## Evidence
- Config regeneration logs show: `Regenerated zerochain.cfg for node 1`
- But bash check inside container shows: `FILE NOT FOUND` or file exists with OLD content
- `mempool proc` returns `processed: true` but datum remains in mempool (indicating `is_add_directly: false`)

## Solution Options

### Option 1: Use stop + start instead of restart
```yaml
- docker_op: stop
  services: "{{_active_nodes}}"
  
- docker_op: start
  services: "{{_active_nodes}}"
```

### Option 2: Send SIGHUP to cellframe-node process
Requires cellframe-node to support configuration reload on SIGHUP (NOT currently implemented in SDK).

### Option 3: Kill process inside container to trigger restart
```yaml
- bash: "pkill -9 cellframe-node"
  node: "{{node}}"
```
Docker's restart policy will restart the process with new config.

### Option 4: Make ConfigStep automatically handle restart
ConfigStep could track which services need restart and automatically invoke docker ops.

## Workaround (Current)
Manually use stop + start in scenarios where config changes need to be applied.

## Impact
- **HIGH**: Genesis scenarios fail because `is_add_directly: true` is not applied
- All scenarios using dynamic config changes are affected
- Misleading: logs show "Regenerated" but config is not active

## Related Files
- `tests/stage-env/src/scenarios/step/config.py` - Config regeneration
- `tests/stage-env/src/docker/compose.py` - restart() implementation
- `tests/stage-env/scenarios/genesis/phase1_zerochain.yml` - Affected scenario
