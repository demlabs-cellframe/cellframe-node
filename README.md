# cellframe-node
Cellframe Blockchain node

[Cellframe Wiki](https://wiki.cellframe.net)

## Build

The project uses CMake. To generate a Makefile run in the project root directory `git submodule init && git submodule update --remote && cmake -S . -B build && cd ./build && make`.
Or if you don't clone the project yet, run `git clone --recursive <repo>` to clone it with all submodules. Then build the project as a regular CMake project with command `cmake -S . -B build && cd ./build && make`.

##How to install:

### Debian and Ubuntu

Create file /etc/apt/sources.list.d/demlabs.list with one line below:

deb http://debian.pub.demlabs.net/ stretch main non-free

Then download public signature and install it:

wget https://debian.pub.demlabs.net/demlabskey.asc
apt-key add demlabskey.asc

Then update your apt cache and install the package:

apt-get update
apt-get install cellframe-node


### Prerequsites

To successfully complete of the build, you must have following prerequisites preinstalled (packages are named as in Debian GNU/Linux 10 "buster", please found the corresponding packages for your distribution):

* libjson-c-dev
* libsqlite3-dev
* libmemcached-dev (for libdap-server-core submodule)
* libev-dev (for libdap-server-core submodule)
* libmagic-dev (for libdap-server submodule)
* libcurl4-openssl-dev | libcurl4-nss-dev | libcurl4-gnutls-dev (for libdap-server submodule)
* libldb-dev
* libtalloc-dev
* libtevent-dev
