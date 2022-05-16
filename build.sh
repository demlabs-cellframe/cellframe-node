#!/bin/bash

if [ ${0:0:1} = "/" ]; then
	HERE=`dirname $0`
else
	CMD=`pwd`/$0
	HERE=`dirname ${CMD}`
fi
apt-get update
 apt-get install -y cmake \
    python \
    libsqlite3-dev \
    libmemcached-dev \
    libev-dev \
    libdbi-dev \
    libsqlite3-dev \
    libcurl4-gnutls-dev \
    libconfig-dev \
    libmagic-dev \
    libcurl4-gnutls-dev \
    libldb-dev \
    libtalloc-dev \
    libtevent-dev \
    traceroute \
    libpython3-dev \
    libpq-dev \
    debhelper \
    wget \
    lsb-release \
    gcc-aarch64-linux-gnu \
    g++-aarch64-linux-gnu \
    gcc-arm-linux-gnueabihf \
    g++-arm-linux-gnueabihf \
    libjson-c-dev \

mkdir ./build

cd build

cmake ..

make
