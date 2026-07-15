# enc_init legacy / modern compatibility (develop-5.8)

## Problem

develop-5.8 used real node b58 in `enc_init` URL path for modern protocol. Legacy
cellframe-node master and many riemann uplinks expect the placeholder path
`gd4y5yh78w42aaagh` (as on master branch). Empty HTTP responses left FSM stuck on
`ENC/IN_PROGRESS`.

## Behaviour after fix

| Mode | URL path | protocol_version | KEM | Signatures |
|------|----------|------------------|-----|------------|
| Modern (default) | placeholder | 26 | Kyber512 | yes |
| Named path (opt-in) | node b58 | 26 | Kyber512 | yes |
| Legacy global | placeholder | 0 | MSRLN | no |
| Auto fallback | placeholder | 0 | MSRLN | no (one retry per link) |

Modern query parameters and POST body are unchanged. Only URL path selection and
fallback logic were adjusted.

## Configuration (`cellframe-node.cfg`)

```ini
[dap_client]
# Modern handshake with placeholder URL (default, master-compatible)
# enc_init_named_path=false

# Use real node b58 in enc_init path for modern protocol (new peers only)
# enc_init_named_path=true

# After modern enc_init failure, retry once with legacy protocol (default true)
# enc_legacy_auto_fallback=true

# Force legacy for all links (old master VPN / very old nodes)
# legacy_enc_handshake=true
```

## Code entry points

- `dap_client_enc_init_url_path()` — shared URL path builder
- HTTP/WS `handshake_init` — uses shared builder
- `dap_client_fsm` — `enc_legacy_fallback_*` one-shot retry
- `s_http_request_response_unencrypted` — empty body calls `error_callback`
