#! /bin/bash
set -e
STORAGE_URL=https://pub.cellframe.net/linux/cellframe-node/master


MACHINE=$(uname -m)

POSTFIX="amd64"

if [[ $MACHINE = "aarch64" ]]; then
    POSTFIX="arm64"
fi
if [[ $MACHINE = "armv7l" ]]; then
    POSTFIX="armhf"
fi

REGEXP="href=\"cellframe-node-([0-9].[0-9]-[0-9]+)-updtr-${POSTFIX}.deb" 

echo "Looking for regexp: $REGEXP"

INSTALLED_VERSION=$(dpkg -l | awk '$2=="cellframe-node" { print $3 }')

echo "Cellframe-node installed: $INSTALLED_VERSION"


AVAILABLE_VERSIONS=()
for l in $(wget -qO- $STORAGE_URL)
do
    if [[ $l =~ $REGEXP ]]
    then
        AVAILABLE_VERSIONS+=(${BASH_REMATCH[1]})
    fi
done

echo "Available versions: ${AVAILABLE_VERSIONS[@]}"

REBUILDS=()
for l in ${AVAILABLE_VERSIONS[@]}
do
    REBUILDS+=($(echo $l ))
done

MAX_REBUILD=( $( printf "%s\n"  "${AVAILABLE_VERSIONS[@]}" | cut -c 5-10 | sort -nr ) )
CURRENT_REBUILD=$(echo $INSTALLED_VERSION | grep -Po "[0-9]([0-9]+)")

echo "Available patch: $MAX_REBUILD | Current patch: $CURRENT_REBUILD"

if (( MAX_REBUILD > CURRENT_REBUILD )); then
    # Determine the full version (e.g. 5.3-354) from AVAILABLE_VERSIONS by the patch we found
    for ver in "${AVAILABLE_VERSIONS[@]}"
    do
        patch=$(echo $ver | cut -d'-' -f2)
        if [ "$patch" = "$MAX_REBUILD" ]; then
            NEW_VERSION=$ver
            break
        fi
    done
    echo "Need update cellframe-node to $NEW_VERSION..."
else
    echo "No need to update cellframe-node"
    exit 0
fi

PACKAGE_NAME="cellframe-node-$NEW_VERSION-updtr-${POSTFIX}.deb"
echo "wget"
mkdir -p /tmp/cfupd/
wget $STORAGE_URL/$PACKAGE_NAME -O /tmp/cfupd/$PACKAGE_NAME
echo "wgot"

service cellframe-node stop

#for shure, "service stop" not olways stops the node...
kill -9 `cat /opt/cellframe-node/var/run/cellframe-node.pid` || true


if (( MAX_REBUILD == 250 )); then
    echo "Clear global-db dir..."
    rm /opt/cellframe-node/var/lib/global_db/ -r
else
    echo "No need to clear global_db"
fi



dpkg -i /tmp/cfupd/$PACKAGE_NAME
service cellframe-node restart
