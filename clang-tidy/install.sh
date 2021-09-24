#!/bin/bash
#
# \file  install.sh
# \brief Clang-Tidy - install
#
# https://clang.llvm.org/extra/clang-tidy/
#


set -x

#--------------------------------------------------------------------------------------------------
sudo apt update -y
sudo apt-get install -y --no-install-recommends clang-tidy
#--------------------------------------------------------------------------------------------------
