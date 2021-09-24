#!/bin/sh

. ./common.sh

cd modules

# cppcheck
CXX="${CXX}" ${MAKE} cppcheck JOBS_NUM=${JOBS}
if [ $? != 0 ]; then exit 1; fi

# clang-tidy
CXX="${CXX}" ${MAKE} clang-tidy
if [ $? != 0 ]; then exit 1; fi

cd ..
