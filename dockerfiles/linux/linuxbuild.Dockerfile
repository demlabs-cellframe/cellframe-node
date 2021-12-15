FROM debian:stretch

RUN apt-get -y update && apt-get -y dist-upgrade && \
apt-get install -y build-essential cmake dpkg-dev libpython3-dev libjson-c-dev \
libsqlite3-dev libmemcached-dev libev-dev libmagic-dev libcurl4-gnutls-dev \
libldb-dev libtalloc-dev libtevent-dev traceroute debconf-utils pv
