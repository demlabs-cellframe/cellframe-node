#!/bin/bash

echo "Deploying to $PACKAGE_PATH"
echo $wd

cd build
PKGFILES=($(ls *.deb))
cd ..
mv build/*.deb $wd/$PACKAGE_PATH/ || echo "[ERR] Something went wrong in publishing the package. Now aborting."

NOTONBUILDSERVER=0
gitlab-runner -v 2&>> /dev/null || NOTONBUILDSERVER=$?
if [[ $NOTONBUILDSERVER == 0 ]]; then
	mkdir -p $REPO_DIR_SRC
	for pkgfile in $PKGFILES; do
		cp -v $wd/$PACKAGE_PATH/$pkgfile $REPO_DIR_SRC
	done
	cd $REPO_DIR
	sudo reprepro -C "$DISTR_COMPONENT" --ask-passphrase includedeb "$DISTR_CODENAME" $REPO_DIR_SRC/*.deb
	#Update into reprepro:
	
	#Need to create latest symlink to the project.
fi
	export -n "UPDVER"
rm -r $REPO_DIR_SRC
cd $wd
#symlink name-actual to the latest version.
#build/deb/versions - for all files
#build/deb/${PROJECT}-latest - for symlinks.
