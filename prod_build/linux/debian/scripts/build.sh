#!/bin/bash

WORKDIR="resources/cellframe/cellframe-node"
SCRIPTDIR="prod_build/linux/debian/scripts"

#cd $WORKDIR
	$SCRIPTDIR/compile_and_pack.sh || exit 2 && \
	$SCRIPTDIR/test.sh || exit 3 && \
	$SCRIPTDIR/install_test.sh || exit 4 && \
	$SCRIPTDIR/cleanup.sh || exit 5
#cd $wd
