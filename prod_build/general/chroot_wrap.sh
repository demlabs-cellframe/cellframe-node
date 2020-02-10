#!/bin/bash

export_variables() {

IFS=$'\n'
for variable in $(cat prod_build/$platform/conf/*); do
	[ -z $1 ] && export $(echo "$variable" | sed 's/\"//g') || export -n $(echo $variable | cut -d '=' -f1)
done

}

CHROOT_PREFIX="builder"
CHROOTS_PATH=$1
PLATFORMS=$2
PKG_FORMAT=$3
SRC_PATH=$4
JOB=$5

cd $SRC_PATH
echo "Platforms are $PLATFORMS"


for platform in $PLATFORMS; do
	export_variables
	IFS=' '
	PKG_TYPE=$(echo $PKG_FORMAT | cut -d ' ' -f1)
	#Check if chroots are present
	echo $HOST_DISTR_VERSIONS
	echo $HOST_ARCH_VERSIONS
	[ -e prod_build/$platform/scripts/pre-build.sh ] && prod_build/$platform/scripts/pre-build.sh $CHROOT_PREFIX #For actions not in chroot (version update)
	for distr in $HOST_DISTR_VERSIONS; do
		for arch in $HOST_ARCH_VERSIONS; do
			if [ -e $CHROOTS_PATH/$CHROOT_PREFIX-$distr-$arch ]; then
				schroot -c $CHROOT_PREFIX-$distr-$arch -- launcher.sh prod_build/$platform/scripts/$JOB.sh "$PKG_TYPE" || errcode=$?
#				echo "schroot stub $PKG_TYPE"
			else
				echo "chroot $CHROOT_PREFIX-$distr-$arch not found. You should install it first"
			fi
		done
	done
	[ -e prod_build/$platform/scripts/post-build.sh ] && prod_build/$platform/scripts/post-build.sh #For post-build actions not in chroot (global publish)
	PKG_FORMAT=$(echo $PKG_FORMAT | cut -d ' ' -f2-)
#	export_variables clean
done
#[ $(mount | grep "/run/schroot/mount") ] && sudo umount -l /run/schroot/mount && sudo rm -r /run/schroot/mount/* #Removing mountpoint odds.

cd $wd
