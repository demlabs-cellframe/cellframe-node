#!/bin/bash

echo "Deploying to $PACKAGE_PATH"
echo $wd
cd $REPO_DIR
PKGFILES=($(ls build/*.deb))
mv build/*.deb $wd/$PACKAGE_PATH || echo "[ERR] Something went wrong in publishing the package. Now aborting."

if [ ! -z $UPDVER ]; then
	for pkgfile in $PKGFILES; do
		ln -sf $wd/$PACKAGE_PATH/$pkgfile $wd/$PACKAGE_PATH/$pkgfile-latest
		cp $wd/$PACKAGE_PATH/$pkgfile $REPO_DIR_SRC
	done
	sudo reprepro -c "$DISTR_COMPONENT" --ask-passphrase includedeb "$DISTR_CODENAME" $REPO_DIR_SRC/*.deb
	#Update into reprepro:
	
	export -n "UPDVER"
	#Need to create latest symlink to the project.
fi

cd $wd
#symlink name-actual to the latest version.
#build/deb/versions - for all files
#build/deb/${PROJECT}-latest - for symlinks.
