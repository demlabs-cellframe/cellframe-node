# cellframe-node
Cellframe Node

[Cellframe Node usage Wiki](https://wiki.cellframe.net/index.php/Node_usage)

## Build from sources:

### Prerequsites:

To successfully complete of the build, you must have following prerequisites preinstalled (packages are named as in Debian GNU/Linux 10 "buster", please found the corresponding packages for your distribution):

* libjson-c-dev
* libsqlite3-dev
* libmemcached-dev
* libev-dev
* libmagic-dev
* libcurl4-openssl-dev | libcurl4-nss-dev | libcurl4-gnutls-dev  ( depricated modules, soon will be removed)
* libldb-dev
* libtalloc-dev
* libtevent-dev

### Prepare system
Comamnd to install them all with build tools
```
sudo apt-get install build-essential cmake cpack dpkg-dev libjson-c-dev libsqlite3-dev libmemcached-dev libev-dev libmagic-dev libcurl4-gnutls-dev libldb-dev libtalloc-dev libtevent-dev
```

### Get all sources

This command fetch sources from gitlab and build them. 
  ```
  git clone https://gitlab.demlabs.net/cellframe/cellframe-node.git
  cd cellframe-node
  git submodule init
  git submodule update
  ```

### Build sources
Get into directory with cellframe-node and do
  ```
  mkdir build
  cd build
  cmake ../
  make -j 8
  ```
Thats produce everything in build/ subdirectory.

## Install package

### Prepare for installation (Debian/Ubuntu)
To prepare node for installation we need to produce pacakge. Or - do ```sudo make install``` from build directory, then get config template from ```dist/share/configs``` and produce proper one in ```/opt/celllframe-node/etc```
Anyway we suggest you to produce the package with command ```cpack``` from the build directory.

#### Install from local package
If you downloaded or build from sources a debian pacakge, like ```cellframe-node_2.11-4-buster_amd64.deb``` you need to install it with ```dpkg``` command. Example:
```
dpkg -i -plow  ./cellframe-node_2.11-4-buster_amd64.deb
```
#### Install from DemLabs official public repository

* Create file /etc/apt/sources.list.d/demlabs.list with one line below for Debian 10:
  ```
  deb https://debian.pub.demlabs.net/ buster main
  ```
* For Ubuntu 18 (Bionic):
  ```
  deb https://debian.pub.demlabs.net/ bionic main universe
  ```
* Then download public signature and install it:
  ```
  wget https://debian.pub.demlabs.net/debian.pub.demlabs.net.gpg
  apt-key add demlabskey.asc
  ```
* Then update your apt cache and install the package:
  ```
  apt-get update
  apt-get install cellframe-node
  ```

During installation it asks some questions

#### Debian package questions
All this could be changed after in configs


* Auto online
If true, the node goes online after he starts and then try to keep this state automaticaly 

* Debug mode
If true - produce more log output in files. Suggested to set ```true``` until the testing period 

* Debug stream headers
Dump stream headers in logs, set it ```true``` only if you want to get more debug information about stream packages passing through. Suggested ```false``` for almost everybody

* Accept connections
Enable/disable listening network address. Set ```false``` if you don't want to accept network connections to your node

* Server address
Network address used for listentning. Set ```0.0.0.0``` if you want to listen all network interfaces on your computer

* Server port (optional, usualy don't ask)
Server port, 8079 by default but sometimes better to set it to ```80``` or ```443``` to masquarade service as web service. 

* Kelvin-testnet: Enable network
Set ```true``` if you want to connect your node with ```kelvin-testnet```

* Kelvin-testnet: Node type (role)
Select node type (or node role) from suggested list with short descriptions. By default suggested to select ```full```


## How to run 

### Debian/Ubuntu
If the node is installed in your system you need only to check it if its runned on your system
```
  sudo service cellframe-node status
```
And if its not runned - start it. Start after reboot should be automaticaly executed.
```
  sudo service cellframe-node start
```

To stop it use the next command:
```
  sudo service cellframe-node start
```
 
