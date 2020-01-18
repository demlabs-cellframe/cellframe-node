# cellframe-node
Cellframe Blockchain node

[Cellframe Wiki](https://wiki.cellframe.net)

## Build:

* The project uses CMake. To generate a Makefile run in the project root directory:
  ```
  git submodule init
  git submodule update --remote
  cmake -S . -B build && make -C build
  ```
* Or if you don't clone the project yet:
  ```
  git clone --recursive <repo>
  cmake -S . -B build && make -C build
  ```

## How to install:

### Debian and Ubuntu:

* Create file /etc/apt/sources.list.d/demlabs.list with one line below:
  ```
  deb https://debian.pub.demlabs.net/ stretch main non-free
  ```
* For Ubuntu 18.04 (Bionic):
  ```
  deb https://debian.pub.demlabs.net/ bionic main universe multiverse
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

### Prerequsites:

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
