#!/bin/bash

set -x
DISTR_COMPONENT=$1
DISTR_CODENAME=$2
PKGNAME=$3
PATH=$4

workdir=$(pwd)
error=0
cd $PATH
ls /usr/bin | grep "reprepro"
/usr/bin/reprepro -C "$DISTR_COMPONENT" --ask-passphrase includedeb "$DISTR_CODENAME" "$PKGNAME" && /usr/bin/reprepro export "$DISTR_CODENAME" || error=$?
cd $workdir
exit $error
set +x
