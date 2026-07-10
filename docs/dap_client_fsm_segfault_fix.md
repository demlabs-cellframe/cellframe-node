# SIGSEGV in dap_client_fsm (use-after-free)

## Symptom

Node crash in `s_fsm_process()` at `dap_client_fsm.c:1023` when accessing
`a_fsm->client->stage_status_error_callback` on FSM thread pool worker.

Typical log sequence before crash:

```
Handshake esocket deleted while stage ENC in progress
Disconnect state(STREAM_ABORTED), all transports exhausted, doing callback
client_error_cb disconnected ... client=ENC/ERROR
link_drop attempts exhausted
FSM stage ENC completed (target: STREAM)   <-- stale notification
FSM dispatching stage STREAM_CTL
link_drop delete link
link_delete drop client / link_drop_io
Disconnect state(STREAM_ABORTED) ...       <-- second notification on freed client
SIGSEGV in s_fsm_process
```

## Root cause

Race between FSM thread and asynchronous link teardown:

1. Handshake esocket is deleted during `ENC` → `dap_client_fsm_notify(ERROR)`.
2. FSM processes terminal error, calls `stage_status_error_callback` →
   `s_client_error_callback` → `s_link_drop_callback` is queued on proc thread
   (**async**, client still alive).
3. Before `link_drop` deletes the client, another FSM notification
   (stale `STAGE_STATUS_DONE` from handshake) is processed → FSM advances to
   `STREAM_CTL`.
4. `link_drop` / `link_delete` calls `dap_client_delete_mt()` → client freed.
5. Next `STAGE_STATUS_ERROR` (from `STREAM_CTL` failure) runs `s_fsm_process`
   with dangling `a_fsm->client` pointer → **SIGSEGV**.

`is_removing` was set only inside `dap_client_delete_mt()`, too late to block
queued FSM tasks. On Linux `s_is_valid_ptr()` is a NULL check only, so a freed
client pointer is not detected.

## Fix

In `dap_client_fsm.c`:

1. Set `a_fsm->is_removing = true` **before** terminal error callback — blocks
   stale notifications still in the FSM thread queue.
2. Add `s_fsm_client_bound()` — verify `client->_internal` still points to FSM.
3. Use binding check in `s_fsm_process()` and `s_fsm_notify_on_fsm_thread()`.
4. Clear `a_fsm->client = NULL` in `dap_client_fsm_delete_unsafe()`.

## Related config

Connection failures to uplink `64.226.102.206:8079` are a separate issue
(handshake abort / empty HTTP response). See `docs/links_connecting_diag.md`.
