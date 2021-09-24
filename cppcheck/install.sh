#!/bin/bash
#
# \file  install.sh
# \brief Cppcheck - build/install
#
# https://github.com/danmar/cppcheck
#


set -x

#--------------------------------------------------------------------------------------------------
VERSION=2.5

git clone --depth=1 https://github.com/danmar/cppcheck.git

cd cppcheck
# git checkout tags/${VERSION}

mkdir build
cd build

cmake \
	-DCMAKE_DISABLE_PRECOMPILE_HEADERS=ON \
	../

sudo cmake \
	--build . \
	--parallel 4 \
	--target install \
	--clean-first
#--------------------------------------------------------------------------------------------------
