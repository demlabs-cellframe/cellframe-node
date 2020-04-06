#!/bin/bash

check_packages() {

	IFS=" "
	local PKG_DEPPIES=$(echo $PKG_DEPS | sed 's/\"//g')
	for element in "$PKG_DEPPIES"; do
		echo "[DEBUGGA] Checking if $element is installed"
		if ! dpkg-query -s $element; then 
			echo "[WRN] Package $element is not installed. Starting installation"
			return 1
		fi
	done
	return 0

}

install_dependencies() {

	echo "Checking out the dependencies"
	if check_packages >> /dev/null; then
		echo "[INF] All required packages are installed"
	else
		echo ""
		local PKG_DEPPIES=$(echo $PKG_DEPS | sed 's/\"//g')
		echo "[DEBUGGA] Attempting to install $PKG_DEPPIES"
		if sudo apt-get install $PKG_DEPPIES -y ; then
			echo ""
			echo "[INF] Packages were installed successfully"
		else
			echo "[ERR] can\'t install required packages. Please, check your package manager"
			echo "Aborting"
			exit 1
		fi
	fi
	return 0

}
PKG_DEPS=$1
install_dependencies
exit 0
#for variable in $(cat ./prod_build/general/conf/brands | sed 's/\"//g'); do
#	echo $variable
#	export "$variable"
#done
