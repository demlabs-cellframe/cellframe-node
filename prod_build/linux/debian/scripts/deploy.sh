#!/bin/bash

echo "Deploying to $PACKAGE_PATH"
echo $wd
PKGFILES=($(ls build/*.deb))
mv build/*.deb $wd/$PACKAGE_PATH || echo "[ERR] Something went wrong in publishing the package. Now aborting."

if [ ! -z $UPDVER ]; then
	for pkgfile in $PKGFILES; do
		ln -sf $wd/$PACKAGE_PATH/$pkgfile $wd/$PACKAGE_PATH/$pkgfile-latest
	done
	export -n "UPDVER"
	#Need to create latest symlink to the project.
fi

#symlink name-actual to the latest version.
#build/deb/versions - for all files
#build/deb/${PROJECT}-latest - for symlinks.
