# Plugin CLI commands in `plugin show`

## Problem

Plugin-specific CLI commands (`vpn_cdb`, `demo`, etc.) are registered at runtime via
`dap_cli_server_cmd_add()` or `AppCliServer.cmdItemCreate()`. They appear as separate
entries in `help`, but there was no way to discover which commands belong to a plugin
from the `plugin` management command.

## Solution

The `params` array in `manifest.json` lists CLI command names provided by the plugin.
`plugin show <name>` reads this field and prints a **CLI commands** section.

For each command name:

- If the command is registered in CLI and has `doc`, the short description is shown.
- If registered without `doc`, a hint to run `help <command>` is shown.
- If not registered yet (plugin not loaded), the entry is marked as not registered.

## Manifest example

```json
{
    "type": "binary",
    "name": "vpn-cdb",
    "version": "2.9.0",
    "author": "DEMLABS",
    "dependencies": [],
    "description": "VPN Central DataBase plugin",
    "params": ["vpn_cdb", "cdb_auth", "cdb_news"]
}
```

## Usage

```bash
cellframe-node-cli plugin show vpn-cdb
cellframe-node-cli help vpn_cdb
```

## Notes

- `params` must be maintained in the manifest by the plugin author.
- Commands are registered only after the plugin loads successfully (`plugin_init` / Python `init()`).
- General `help` still shows only short descriptions; use `help <command>` for full syntax.
