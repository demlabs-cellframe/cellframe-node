# cellframe-node
Cellframe Blockchain node

[![Build Status](https://travis-ci.com/osetrovich/kelvin-node-ci.svg?branch=master)](https://travis-ci.com/osetrovich/kelvin-node-ci)

[Cellframe node manual](https://github.com/cellframe/kelvin-node/wiki/Kelvin-Node)

## Build

The project uses CMake. To generate a Makefile run in the project root directory `git submodule init && git submodule update --remote && cmake -S . -B build && cd ./build && make`.
Or if you don't clone the project yet, run `git clone --recursive <repo>` to clone it with all submodules. Then build the project as a regular CMake project with command `cmake -S . -B build && cd ./build && make`.

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
