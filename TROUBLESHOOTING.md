# Troubleshooting / FAQ

## Where are the configuration files located?

Cellframe node uses `/opt/cellframe-node/etc/cellframe-node.cfg` file as it's configuration file.
For different networks, configuration files are placed in `/opt/cellframe-node/etc/network/`.

## Where are the log files located?

By default, Cellframe node log file can be found at `/opt/cellframe-node/var/log/cellframe-node.log`.

## How to remove Cellframe node?

**NOTE: Be careful, take a backup of your created wallets from `/opt/cellframe-node/var/lib/wallet/` before proceeding!**

On Debian and it's derivatives, you can use `apt remove cellframe-node` and delete folder `/opt/cellframe-node` after removal. 

On other Linux systems:
```
sudo systemctl stop cellframe-node.service
sudo systemctl disable cellframe-node.service
sudo unlink /etc/logrotate.d/cellframe-node
sudo unlink /etc/profile.d/cellframe-node.sh
sudo rm -rf /opt/cellframe-node
```

## Running and debugging in Qt (Linux Mint)

During debugging, the configuration files located in /opt/cellframe-node/ are used. Therefore, it is necessary to grant access rights to this directory to the user who will do the debugging.

```
sudo chown user_name /opt/cellframe-node/
```
