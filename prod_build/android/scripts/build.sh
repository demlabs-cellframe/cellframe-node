#!/bin/bash

. ./prod_build/general/pre-build.sh
export_variables "./prod_build/android/conf/*"

#read_conf.
#src_path=$workdir/resources/SAP/sapnet-client
#WORK_PATH=$wd/resources/SAP/sapnet-client-build
SRC_DIR=$(pwd)
RES_PATH=${SRC_DIR}/$RES_PATH
exitcode=0

echo "DexGuard tuning"
[ -f "$RES_PATH/gradle.properties" ] || { echo "systemProp.dexguard.license=/usr/local/etc/dexguard-license.txt" >> $RES_PATH/gradle.properties && echo "enableDexGuard=true" >> $RES_PATH/gradle.properties ; }
sed -i '/flatDir/s/'"'"'.*'"'"' }/'"'"'\/opt\/DexGuard\/DexGuard-8.2.12\/lib'"'"' }/' $RES_PATH/build.gradle
mkdir -p $SRC_DIR/build/apk


BRAND=`cat *.pro | grep "BRAND " | rev | cut -d " " -f1 | rev`
echo "extracting version"
VERSION=$(extract_version_number)
echo "version number is $VERSION"
. prod_build/android/essentials/key/creds.conf

mkdir -p $WORK_PATH
cd $WORK_PATH
rm -rf *
APK_PATH=android/build/outputs/apk
echo "arch-versions are $ARCH_VERSIONS"
IFS=" "
for arch in $ARCH_VERSIONS; do
	 mkdir -p $arch
	 cd $arch
	export QT_SELECT=$arch
	ANDRQT_HOME=/usr/lib/crossdev/android-$arch/*/bin
	$ANDRQT_HOME/qmake -r -spec android-g++ CONFIG+=release CONFIG+=qml_release BRAND=$BRAND BRAND_TARGET=$BRAND $SRC_DIR/*.pro && \
	$ANDROID_NDK_HOME/prebuilt/$NDKHOST/bin/make -j3 && \
	$ANDROID_NDK_HOME/prebuilt/$NDKHOST/bin/make install INSTALL_ROOT=$(pwd)/android && \
	echo "Deploying in " && pwd && $ANDRQT_HOME/androiddeployqt --output android --verbose --input SapNetGui/*.json --sign $SRC_DIR/prod_build/android/essentials/key/release-key.jks $ALIAS --storepass $PASS --jdk $JAVA_HOME --gradle && \
	mv -v $(pwd)/$APK_PATH/android-release-signed.apk $SRC_DIR/build/apk/"$BRAND-${VERSION}_$arch.apk" || \
	exitcode=$?
	cd ..
	if [[ $exitcode != 0 ]]; then
		echo "Build failed with exit code $exitcode"
		cd $workdir
		exit $exitcode
	fi
done

cd $workdir
