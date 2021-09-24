# Analysis

## Prerequisites

FreeBSD:

Linux:

- sudo pkg install git pkg-config python

## Cppcheck

http://cppcheck.sourceforge.net/

FreeBSD:

- sudo pkg install cppcheck-1.89

Linux:

- sudo apt-get install cppcheck (1.84)
- sudo snap install cppcheck (1.87)

Suppressions

- cppcheck --errorlist

## Clang-Tidy

https://clang.llvm.org/extra/clang-tidy/

FreeBSD:

- sudo pkg install llvm90-9.0.0
- sudo ln -s /usr/local/llvm90/bin/clang-tidy /usr/local/bin/clang-tidy

Linux:

- sudo apt-get install clang-tidy

Links:

- https://zed0.co.uk/clang-format-configurator/
- https://github.com/llvm-mirror/clang-tools-extra/blob/master/clang-tidy/tool/clang-tidy-diff.py
- https://chromium.googlesource.com/chromium/src.git/+/HEAD/tools/clang/scripts/clang_tidy_tool.py
- https://devhub.vr.rwth-aachen.de/vlopatin/Project_Phoenix/blob/4b36eddc10d92e9f7a1ca087860285160d3931e7/cmake/execute_clang_tidy.cmake

Suppressions

- clang-tidy -checks='*' --list-checks
- clang-tidy -dump-config

Notes:

- -j (--jobs) - not supported option

## Git hooks

- install Git hooks

```bash
git-hooks-install.sh
```

- clang-tidy, check single file:

```bash
cd analysis/git-hooks
python pre-commit-analysis.py --file-to-check=/home/httpd/triptake-all/syntexts/modules/cms_content_gen.cc
```
