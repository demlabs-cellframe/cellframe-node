# Troubleshooting / FAQ

## Where are the configuration files located?

Cellframe node uses `/opt/cellframe-node/etc/cellframe-node.cfg` file as it's configuration file.
For different networks, configuration files are placed in `/opt/cellframe-node/etc/network/`.

## Where are the log files located?

By default, Cellframe node log file can be found at `/opt/cellframe-node/var/log/cellframe-node.log`.

## Running and debugging in Qt (Linux Mint)

During debugging, the configuration files located in /opt/cellframe-node/ are used. Therefore, it is necessary to grant access rights to this directory to the user who will do the debugging.

```
sudo chown user_name /opt/cellframe-node/
```
