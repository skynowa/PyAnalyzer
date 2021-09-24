#!/bin/sh


ln -s ../../analysis/git-hooks/pre-commit-analysis.py ../.git/hooks/pre-commit
if [ $? -ne 0 ]; then
    echo "pre-commit - fail"
fi

ln -s analysis/git-hooks/clang-tidy/config_local.yaml ../.clang-tidy
if [ $? -ne 0 ]; then
    echo ".clang-tidy - fail"
fi

ln -s options_local.py git-hooks/options.py
if [ $? -ne 0 ]; then
    echo ".clang-tidy - fail"
fi

echo "OK"
