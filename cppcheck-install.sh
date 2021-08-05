#!/bin/bash
#
# \file  cppcheck-install.sh
# \brief Cppcheck - build/install
#
# https://github.com/danmar/cppcheck
#


set -x

#--------------------------------------------------------------------------------------------------
VERSION=2.5

git clone https://github.com/danmar/cppcheck.git

cd cppcheck
git checkout tags/${VERSION}

mkdir build
cd build

cmake \
	-DCMAKE_DISABLE_PRECOMPILE_HEADERS=ON \
	../

sudo cmake \
	--build . \
	--target install \
	--clean-first
#--------------------------------------------------------------------------------------------------
