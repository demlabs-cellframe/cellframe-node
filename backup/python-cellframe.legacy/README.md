# python-cellframe

## Prerequisites
To install, you must have Python3.7 including pip and a scikit-build.
sudo apt-get install pip3
If there is a problem on Debian buster 
"unknown system group 'Debian-exim' in statoverride file; the system group got removed"
Use the following command to fix it
dpkg-statoverride --remove /etc/exim4/passwd.client
Now repeat sudo apt-get install pip3

## Build:
```
git clone https://gitlab.demlabs.net/cellframe/python-cellframe.git
cd python-cellframe
git submodule update --init 
cd cellframe-sdk
git submodule update --init
cd ..
sudo python3.7 setup.py install
```

## How to package 
First install packages 
```
apt-get install devscripts dpkg-dev build-essential libmagic-dev libjson-c-dev libjsoncpp-dev  libsqlite3-dev traceroute libverto-dev libpython3-dev cmake

```


## Windows Build
First of all you need to install msys2. It provides 3 shells.
To install dependencies, run from MSYS shell:
```
pacman -S base-devel mingw-w64-x86_64-toolchain mingw-w64-x86_64-cmake mingw-w64-x86_64-file mingw-w64-x86_64-json-c mingw-w64-x86_64-python-pip
```

To start a build, run from MinGW 64bit shell (don't forget to change dir to python-cellframe repo):
```
python setup.py install
```
