# Links connecting diagnostics

> **Temporary debug code.** Marked in sources with `TEMP_DEBUG_LINKS_CONNECTING`.
> To remove after investigation: `rg TEMP_DEBUG_LINKS_CONNECTING` and delete all marked blocks;
> also remove this file and config key `links_connecting_diag_interval`.

Diagnostic logging for `NET_STATE_LINKS_CONNECTING` stalls.

## Configuration

In `cellframe-node.cfg` or network config:

```ini
[link_manager]
# Periodic uplink snapshot interval in seconds (default 30, 0 = disable)
links_connecting_diag_interval=30
```

## When logs appear

1. **On transition to CONNECTING** — immediate snapshot for the network.
2. **Every `links_connecting_diag_interval` seconds** — log prefix `[TEMP_DEBUG]`, while `established < links_required` or when ESTABLISHED uplinks skip `connected` callback because they are still in link cluster.
3. **On each `LINK_CONNECTED` event** — if count is still below `links_required`:
   ```
   riemann still NET_STATE_LINKS_CONNECTING: established 1/3 after LINK_CONNECTED
   ```

## Example log

```
Links connecting diag net 0x...: required=3 manager_active=1 max_attempts=1 reconnect_delay=20s
  cluster_members=2 pending_uplinks=2 needed_new=1
  uplink 0x... 178.128.255.95:80 state=CONNECTING cluster=no client=ENC/IN_PROGRESS attempts=0 wait=0s
  uplink 0x... 10.0.0.1:8045 state=DISCONNECTED cluster=yes client=BEGIN/NONE attempts=1 wait=12s
  summary: established=0/3 connecting=1 disconnected=1 no_host=0 cluster_cb_skip=0 delay_cb_skip=0
  likely cause: uplinks failed or waiting reconnect_delay; check HTTP/stream handshake errors in log
```

## Grep in log

```bash
grep '\[TEMP_DEBUG\]' cellframe-node.log
```

### Event tags

| Tag | Meaning |
|-----|---------|
| `link_connect start` | Outbound connect initiated |
| `link_update auto connect` | Host/port applied, connect starting |
| `client_connected_cb OK` | FSM reached STREAM, link ESTABLISHED |
| `client_error_cb` | FSM error, drop scheduled |
| `link_drop *` | Drop/retry/delete path |
| `link_drop_io` | Client delete without links_lock |
| `HTTP empty response` | HTTP handshake got zero bytes |
| `wake_up connected_cb skipped` | ESTABLISHED but node still in cluster |
| `links_request` | Balancer request triggered |

### Field reference

| Field | Meaning |
|-------|---------|
| `required` | `general.links_required` from network config |
| `pending_uplinks` | Links counted toward minimum (cluster members + associated pending) |
| `pending_outbound` | Client links with `is_uplink=0` (not yet in official established count) |
| `established_official` | From `dap_link_manager_established_uplinks_count()` |
| `is_uplink` | Becomes 1 after outbound stream is authorized |
| `needed_new` | How many more uplinks balancer should request |
| `cluster=yes` | Node still in link cluster (may block `LINK_CONNECTED` event on reconnect) |
| `wait=Ns` | Seconds until reconnect or `connected` callback allowed |
| `connected_cb_skipped: already in cluster` | Stream up but state machine won't get `LINK_CONNECTED` |
| `cluster_cb_skip` | Count of ESTABLISHED uplinks blocked by cluster membership |

## Likely causes in summary line

- **cluster after reconnect** — enough ESTABLISHED links but no `LINK_CONNECTED` events
- **handshake / reconnect_delay** — connection failures, see `Connect failed`, `empty response` in log
- **no host/port** — node missing in GDB or `permanent_nodes` config
- **balancer** — `pending_uplinks` below required, no new nodes requested
