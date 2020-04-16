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


substitute_pkgname_postfix() {

	#CODENAME=$(lsb_release -a | grep Codename | cut -f2)
	#VERSION=$(lsb_release -a | grep Version | cut -f2)
	#DISTRO_TYPE=$(lsb_release -a | grep Distributor | cut -f2)
	for variable in $(lsb_release -a 2>/dev/null | sed 's/\t//g' | sed 's/ //g' | sed 's/\:/\=/g'); do
		echo "variable is $variable"
		export $variable
	done
	sed -i "/ CPACK_SYSTEM_TYPE/s/\".*\"/\"$DistributorID\"/" CMakeLists.txt
	sed -i "/ CPACK_SYSTEM_VERSION/s/\".*\"/\"$Release\"/" CMakeLists.txt
	sed -i "/ CPACK_SYSTEM_CODENAME/s/\".*\"/\"$Codename\"/" CMakeLists.txt
#	sed -i "/ CPACK_SYSTEM_ARCH/s/\".*\"/\"$Codename\"/" CMakeLists.txt No need to replace anything while we're on amd64 arch only.
	export -n "DistributorID"
	export -n "Release"
	export -n "Codename"
	export -n "Description"
}

repack() {

DEBNAME=$1
DISTR_CODENAME="$Codename"
echo "Renaming controlde on $DEBNAME"
mkdir tmp && cd tmp

#Просматриваем архив и ищем строку с control.tar
#Результат заносим в переменную
CONTROL=$(ar t ../${DEBNAME} | grep control.tar)

ar x ../$DEBNAME $CONTROL
tar xf $CONTROL
VERSION=$(cat control | grep Version | cut -d ':' -f2)
echo "Version is $VERSION"
sed -i "s/$VERSION/${VERSION}-${DISTR_CODENAME}/" control
rm $CONTROL && tar zcf $CONTROL *
ar r ../$DEBNAME $CONTROL
cd ..
rm -rf tmp

}

pwd
error=0
mkdir -p packages

substitute_pkgname_postfix && mkdir -p build && cd build && cmake ../ && make -j$(nproc) && cpack && repack *.deb && mv -v *.deb ../packages/ && cd .. && rm -r build || error=$?
exit $error

### touch /etc/apt/sources.list.d/demlabs.list deb https://debian.pub.demlabs.net/ bionic main universe multiverse

### wget https://debian.pub.demlabs.net/debian.pub.demlabs.net.gpg
### apt-key add demlabskey.asc

### apt-get update
### apt-get install cellframe-node



