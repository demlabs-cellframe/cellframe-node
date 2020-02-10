#!/bin/bash

#if [ "$1" == "--static" ]; then
#	export $QT_SELECT="qtstatic" #For static builds we'll have a special qt instance, which should be installed manually for now, unfortunately.
#fi

# error_explainer() {

#	case "$1" in
#		"1"	) echo "Error in pre-config happened. Please, review logs";;
#		"2"	) echo "Error in compilation happened. Please, review logs";;
#		*	) echo "Unandled error $1 happened. Please, review logs";;
#	esac
#	exit $1

# }



### dpkg-buildpackage -J -us --changes-option=--build=any -uc && mkdir -p build && mv ../*.deb build/ && make distclean || error=$? && make distclean && $(error_explainer $error) #2DO: Learn how to sign up the package.

# if [ "$1" == "--static" ]; then
 #	export $QT_SELECT="default" #Returning back the shared library link
  #fi


#cmake -S . -B build && make -C build && cpack -B build
pwd
mkdir -p build && cd build && cmake ../ && make -j3 && cpack && cd ..

### touch /etc/apt/sources.list.d/demlabs.list deb https://debian.pub.demlabs.net/ bionic main universe multiverse

### wget https://debian.pub.demlabs.net/debian.pub.demlabs.net.gpg
### apt-key add demlabskey.asc

### apt-get update
### apt-get install cellframe-node

