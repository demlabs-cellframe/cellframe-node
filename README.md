# kelvin-node
Kelvin Blockchain node

[![Build Status](https://travis-ci.com/cellframe/kelvin-node.svg?branch=master)](https://travis-ci.com/cellframe/kelvin-node)

[Kelvin node manual](https://github.com/cellframe/kelvin-node/wiki/Kelvin-Node)

## Build

The project uses CMake. To generate a Makefile run in the project root directory `git submodule init && git submodule update --remote && cmake .`.
Or if don't clone the project yet, run `git clone --recursive <repo>` to clone it with all submodules. Then build the project as a regular CMake project.

### Prerequsites

To successfully complete of the build, you must have folgende prerequisites installed (packages are named as in Debian GNU/Linux 10 "buster", please found the corresponding packages for your distribution):

* libjson-c-dev

* libmemcached-dev (for libdap-server-core submodule)

* libev-dev (for libdap-server-core submodule)

* libmagic-dev (for libdap-server submodule)

* libcurl4-openssl-dev | libcurl4-nss-dev | libcurl4-gnutls-dev (for libdap-server submodule)
