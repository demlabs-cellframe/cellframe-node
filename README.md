# Build Cellframe node

## 1. Install necessary dependencies

To successfully build Cellframe node, you need to have all the necessary dependencies installed.

On Debian / Ubuntu:
```
sudo apt install build-essential cmake dpkg-dev libpython3-dev libjson-c-dev libsqlite3-dev libmemcached-dev libev-dev libmagic-dev libcurl4-gnutls-dev libldb-dev libtalloc-dev libtevent-dev traceroute debconf-utils pv git logrotate
```

On MacOS:

Install latest XCode from App Store or directly from official Apple site and install Homebrew from brew.sh. If you have Apple silicon chipset, please setup it to /opt/homebrew as recommended on the Homebrew website
After that, install necessary dependencies with:
```
brew install cmake sqlite3
```

## 2. Download the source code with Git
```
git clone https://gitlab.demlabs.net/cellframe/cellframe-node.git --recurse-submodules
cd cellframe-node
```

## 3. Build Cellframe node using CMake framework and install Cellframe node
Use the following commands (separately) to build the node:
```
mkdir build
cd build
cmake ../
make -j$(nproc)
```
After build process has finished, you may create an installation package for Debian and it's derivatives with the command `cpack` and install it with:
```
apt install ./<name-of-the-file>.deb
```
And on other Linux systems:
```
sudo make install
```
When installing from a .deb package, the installer will ask you some [questions](#questions).

# Install from Demlabs official public repository

**NOTE: Currently only the following distros are supported:**
- Debian 11 (Bullseye)

## 1. Add Demlabs public key to your trusted keys with the command:
  ```
  wget -O- https://debian.pub.demlabs.net/public/public-key.gpg | gpg --dearmor | sudo tee /usr/share/keyrings/demlabs-archive-keyring.gpg
  ```

## 2. Add Demlabs repository to your sources with the following command:
  ```
  echo "deb [signed-by=/usr/share/keyrings/demlabs-archive-keyring.gpg] https://debian.pub.demlabs.net/public $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/demlabs.list
  ```
## 3. Update your package index files and install the Cellframe node
  ```
  sudo apt update && sudo apt install cellframe-node
  ```
<a name="questions"></a>During installation the installer will ask you some questions:

* Auto online (true / false)
  * True: Cellframe node goes online after startup and tries to keep this state automatically
  * False: Node stays offline after startup

* Debug mode (true / false)
  * True: Enable debug output to log files
  * False: Disable debug output to log files

* Accept connections (true / false)
  * True: Enable listening network address and accept inbound connections
  * False: Disable listening network address and refuse inbound connections

* Server address
  * Network address used for listening. Set to `0.0.0.0` if you want to listen on all network interfaces on your computer

* Server port
  * Server port to listen on: Default is 8080, recommended 8080. Use 80 or 443 if you want to masquerade node for example as a web service

* Notify server address
  * Default is 127.0.0.1, recommended 127.0.0.1

* Notify server port
  * Default is 8080, recommended 8080

* Enable Subzero testnet (true / false)
  * True: Connect your node to Subzero testnet
  * False: Don't connect your node to Subzero testnet

* Subzero node role (full / light / master / archive / root)
  * Different role types for node. Default `full`, recommended `full`

* Enable KelVPN Minkowski testnet (true / false)
  * True: Connect your node to KelVPN Minkowski testnet
  * False: Don't connect your node to KelVPN Minkowski testnet

* KelVPN Minkowski node role (full / light / master / archive / root)
  * Different role types for node. Default `full`, recommended `full`

* Enable Backbone mainnet (true / false)
  * True: Connect your node to Backbone mainnet
  * False: Don't connect your node to Backbone mainnet

* Backbone node role (full / light / master / archive / root)
  * Different role types for node. Default `full`, recommended `full`

* Enable Mileena testnet (true / false)
  * True: Connect your node to Mileena testnet.
  * False: Don't connect your node to Mileena testnet.

* Mileena testnet node role (full / light / master / archive / root)
  * Different role types for node. Default `full`, recommended `full`

* Enable Python plugins (true / false)
  * True: Enable support for python plugins
  * False: Disable support for Python plugins

* Python plugins path
  * Set path where you want to store your Python plugins.

# Community maintained packages

[Arch Linux](https://aur.archlinux.org/packages/cellframe-node)

# Additional configuration and general FAQ / Troubleshooting
For additional information about configuration: [CONFIGURATION.md](CONFIGURATION.md).

For troubleshooting and general FAQ: [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

# Running your own services on Cellframe network

For information how to run your own services on Cellframe network: [SERVICES.md](SERVICES.md).