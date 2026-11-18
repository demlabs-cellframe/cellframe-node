#! /bin/bash
set -e
STORAGE_URL=https://pub.cellframe.net/linux/cellframe-node/master
# Public Demlabs release key, shipped in /opt/cellframe-node/share/apt/demlabskey.gpg
GPG_KEY=/opt/cellframe-node/share/apt/demlabskey.gpg

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

# Numeric patch sort: "5.3-354" -> 354, compared as integers (the old
# lexicographic `cut -c 5-10 | sort -nr` mis-ordered multi-digit patches)
MAX_REBUILD=0
NEW_VERSION=""
for ver in "${AVAILABLE_VERSIONS[@]}"
do
    patch=$(echo "$ver" | cut -d'-' -f2)
    if (( patch > MAX_REBUILD )); then
        MAX_REBUILD=$patch
        NEW_VERSION=$ver
    fi
done
CURRENT_REBUILD=$(echo "$INSTALLED_VERSION" | grep -Po "[0-9]+$" || echo 0)

echo "Available patch: $MAX_REBUILD | Current patch: $CURRENT_REBUILD"

if (( MAX_REBUILD > CURRENT_REBUILD )); then
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

# Integrity: the package is installed as root — verify the publisher's
# detached signature when it is published. Transitional mode: without a
# signature file we proceed with a loud warning; once pub.cellframe.net
# publishes .sig for every .deb this branch must be removed (fail closed).
if wget -q $STORAGE_URL/$PACKAGE_NAME.sig -O /tmp/cfupd/$PACKAGE_NAME.sig; then
    if [ ! -r "$GPG_KEY" ]; then
        echo "[!] FATAL: publisher key $GPG_KEY is missing, refusing unsigned-in-fact update" >&2
        exit 1
    fi
    if ! gpg --no-default-keyring --keyring "$GPG_KEY" --verify /tmp/cfupd/$PACKAGE_NAME.sig /tmp/cfupd/$PACKAGE_NAME; then
        echo "[!] FATAL: GPG signature verification failed for $PACKAGE_NAME" >&2
        exit 1
    fi
    echo "[+] Package signature verified"
else
    echo "[!] WARNING: no detached signature published for $PACKAGE_NAME;" >&2
    echo "[!] WARNING: installing the package WITHOUT cryptographic verification." >&2
    echo "[!] WARNING: this transitional behavior is removed once all builds publish .sig" >&2
fi

service cellframe-node stop

#for shure, "service stop" not olways stops the node...
kill -9 `cat /opt/cellframe-node/var/run/cellframe-node.pid` 2>/dev/null || true

# The server-triggered "patch 250 wipes global_db" branch is removed on
# purpose: a compromised pub host must not be able to erase node databases.

dpkg -i /tmp/cfupd/$PACKAGE_NAME
service cellframe-node restart
