#!/usr/bin/env python

#--------------------------------------------------------------------------------------------------
# \file  options.py
# \brief SA options
#--------------------------------------------------------------------------------------------------


import os
#--------------------------------------------------------------------------------------------------
""" Analyzer types """
TYPE_CPPCHECK   = 1
TYPE_CLANG_TIDY = 2
TYPE_ACTIVE     = TYPE_CLANG_TIDY

""" Set OS environment variable to disable checks
From shell: export PYANALYZER_SKIP_CHECK=1

0 - enable checks
1 - skip checks
"""
SKIP_CHECK = os.environ.get("PYANALYZER_SKIP_CHECK")

""" Source directory """
DIR_SRC = "services"

""" Check mode
0 - check changed files and headers
1 - check only changed files
"""
QUICK_CHECK = 1

""" Disallow committing when errors/warnings occur
0 - allow commit
1 - disallow commit
"""
STOP_ON_FAIL = 0

""" C++ standard """
CPP_STD = "c++17"

"""
Include files for checking
"""
CPP_MASK = {".h", ".hh", ".hpp", ".inl", ".cc", ".cpp", ".cxx"}

""" Excludes """

#--------------------------------------------------------------------------------------------------
