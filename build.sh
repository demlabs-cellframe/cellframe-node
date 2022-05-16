#!/bin/bash

if [ ${0:0:1} = "/" ]; then
	HERE=`dirname $0`
else
	CMD=`pwd`/$0
	HERE=`dirname ${CMD}`
fi

mkdir ./build

cd build

cmake ..

make
