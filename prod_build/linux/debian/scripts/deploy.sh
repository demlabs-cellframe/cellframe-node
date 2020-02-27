#!/bin/bash

repack() {

DEBNAME=$1
echo "Renaming control on $DEBNAME"
mkdir tmp && cd tmp
ar p ../$DEBNAME control.tar.gz | tar -xz
VERSION=$(cat control | grep Version | cut -d ':' -f2)
echo "Version is $VERSION"
sed -i "s/$VERSION/${VERSION}-$DISTR_CODENAME/" control
tar czf control.tar.gz *[!z]
ar r ../$DEBNAME control.tar.gz
cd ..
rm -rf tmp

}

echo "Deploying to $PACKAGE_PATH"
echo $wd

cd build
PKGFILES=($(ls *.deb))
cd ..
mv build/*.deb $wd/$PACKAGE_PATH/ || echo "[ERR] Something went wrong in publishing the package. Now aborting."

#echo "We have $DISTR_CODENAME there"
echo "On path $REPO_DIR_SRC we have debian files."

NOTONBUILDSERVER=0
gitlab-runner -v 2&>> /dev/null || NOTONBUILDSERVER=$?
if [[ $NOTONBUILDSERVER == 0 ]]; then
	mkdir -p $REPO_DIR_SRC
	for pkgfile in ${PKGFILES[@]}; do
	cd $REPO_DIR_SRC
		cp -v $wd/$PACKAGE_PATH/$pkgfile $REPO_DIR_SRC
		for variant in $HOST_DISTR_VERSIONS; do
			ls $pkgfile | grep $variant && DISTR_CODENAME=$variant #Since we add a postfix into every debpackage done, we'll extract it that way.
		done
		repack $pkgfile
		echo "Attempting to add packages into $DISTR_COMPONENT section to $DISTR_CODENAME"
		cd $REPO_DIR
	    sudo reprepro -C "$DISTR_COMPONENT" --ask-passphrase includedeb "$DISTR_CODENAME" $REPO_DIR_SRC/*.deb && sudo reprepro export --ask-passphrase "$DISTR_CODENAME"
	done

	#Update into reprepro:
	
	#Need to create latest symlink to the project.
fi
	export -n "UPDVER"
rm -r $REPO_DIR_SRC
cd $wd
exit 0
#symlink name-actual to the latest version.
#build/deb/versions - for all files
#build/deb/${PROJECT}-latest - for symlinks.
