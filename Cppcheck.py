#!/usr/bin/env python

#--------------------------------------------------------------------------------------------------
# \file  Cppcheck.py
# \brief Run Static Analyzers
#--------------------------------------------------------------------------------------------------


import sys
import os
import signal
import subprocess
import multiprocessing
import re
import json
import time
import argparse

import options
#--------------------------------------------------------------------------------------------------
class Analyzer:
    """ Static code analyzer using Cppcheck, Clang-Tidy """

    """ public """
    def __init__(self, a_type):
        """ Constructor """

        """ Constants """

        """ Project root directory """
        self.PROJECT_DIR = "/home/httpd/services-sync"

        """ Shell colors """
        self.COLOR_RED     = "\033[0;91m"
        self.COLOR_YELLOW  = "\033[0;93m"
        self.COLOR_GREEN   = "\033[0;92m"
        self.COLOR_MAGENTA = "\033[0;95m"
        self.COLOR_NORMAL  = "\033[0m"

        """ Compiler types """
        self.COMPILER_ID_UNKNOWN = 0
        self.COMPILER_ID_CLANG   = 1
        self.COMPILER_ID_GCC     = 2

        """
        Number of jobs (Cppcheck support only)
        """
        self.JOBS_NUM = str(multiprocessing.cpu_count())


        """ current OS """
        self._os_name = os.uname()[0]

        """ analyzer type """
        self._type = a_type

        """ analyzer name """
        names = {
            options.TYPE_CPPCHECK:        "[Cppcheck]",
            options.TYPE_CLANG_TIDY:      "[Clang-Tidy]",
            options.TYPE_CLANG_TIDY_DIFF: "[Clang-Tidy-Diff]",
            options.TYPE_CLANG_TIDY_FILE: "[Clang-Tidy-File]"
        }

        self._name = names[a_type]
        if (self._name == ""):
            self.traceError("Bad type: " + a_type)
            sys.exit(1)

        """ GIT modified files """
        self._git_modified_files = self.getGitModifiedFilesFromCommit()
        if (len(self._git_modified_files) == 0):
            self.traceOk("No changes. OK")
            sys.exit(0)

    def run(self):
        """ Run analysis by type """

        if (options.QUICK_CHECK == 1):
            self.traceOk("Start analysis (quick)...")
        else:
            self.traceOk("Start analysis (full)...")

        out = None

        # profiler
        time_start_sec = time.time()

        if (self._type == options.TYPE_CPPCHECK):
            out = self.runCppcheck()
        else:
            sys.exit(1)

        stdout,stderr = out.communicate()
        stdout_str = stdout.decode("utf8").strip(" \t\r\n")
        stderr_str = stderr.decode("utf8").strip(" \t\r\n")

        # profiler
        time_stop_sec_str = "({0:.2f} sec)".format(time.time() - time_start_sec)

        print(stdout_str)

        # rm extra warning info
        stderr_str = re.sub("^\d+ warnings generated\.", "", stderr_str).strip(" \t\r\n")
        stderr_str = re.sub("^\d+ warnings generated\.", "", stderr_str).strip(" \t\r\n")

        stderr_str = re.sub("^\d+ warnings and \d error generated\.", "", stderr_str).strip(" \t\r\n")
        self.traceError(stderr_str)

        if (self.isError(out, stderr_str)):
            if (options.STOP_ON_FAIL == 1):
                self.traceError("***** Detect errors. Commit stopped ***** " + time_stop_sec_str)
                sys.exit(1)
            else:
                self.traceError("***** Detect errors. Commited ***** " + time_stop_sec_str)
        else:
            self.traceOk("No warnings. OK " + time_stop_sec_str)

    def traceOptions(self):
        """ Trace options (confogs) """

        print("")
        self.traceOk("Options:")
        print("TYPE_ACTIVE: ", self._name)
        print("QUICK_CHECK: ", options.QUICK_CHECK)
        print("SKIP_CHECK:  ", options.SKIP_CHECK)
        print("STOP_ON_FAIL:", options.STOP_ON_FAIL)
        print("CPP_STD:     ", options.CPP_STD)
        print("CPP_MASK:    ", ", ".join(options.CPP_MASK))
        print("cwd:         ", os.getcwd())
        print("")

    """ private """
    def runCppcheck(self):
        """ Run analysis Cppcheck """

        # cmd = \
        #     "cppcheck " \
        #     "{} {} " \
        #     "--library=std.cfg --library=posix.cfg " \
        #     "-UKERN_PROC_PATHNAME " \
        #     "--enable={} --inconclusive " \
        #     "--language=c --language={} --std={} " \
        #     "--platform=unix64 " \
        #     "--force " \
        #     "-j{} " \
        #     "--relative-paths " \
        #     "--error-exitcode=1" \
        #     .format(self._include_dirs, self._git_modified_files, options.CPPCHECK_ERROR_LEVEL,
        #         options.CPP_LANG, options.CPP_STD, self.JOBS_NUM) \
        #     .split()

        cmd = \
            "cppcheck " \
            "--project=./src/services_build/compile_commands.json " \
            "--cppcheck-build-dir=./src/services_build " \
            "--max-configs=1 " \
            \
            "--language=c " \
            "--language=c++ " \
            "--std=c++17 " \
            "--library=std.cfg " \
            "--library=posix.cfg " \
            "--platform=unix64 " \
            \
            "--enable=warning,missingInclude " \
            "--inconclusive " \
            \
            "--suppressions-list={} " \
            \
            "--relative-paths " \
            "--error-exitcode=1 " \
            \
            "--report-progress " \
            "--verbose " \
            \
            "--template='{{severity}}|{{id}}|{{message}}|{{file}}|{{line}}:{{column}}|{{callstack}}|{{code}}' " \
            \
            "-j18 " \
            "--file-filter=/home/httpd/Gitlab/services-sync/src/services/sync/dotw_services_sync.cc" \
            .format( \
                "./suppressions_cppcheck.txt", \
                self._git_modified_files) \
            .split()

        print("cmd: ", cmd)

        return subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)

    def getGitModifiedFilesFromCommit(self):
        """ Get current GIT modified files from commit """

        result = ""

        # Git commit ID
        cmd = "git log --format='%H' -n 1".split()
        # print("cmd: ", cmd)

        out = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        stdout,stderr = out.communicate()

        git_commit_id = stdout.strip().decode("utf8").replace("'", "")
        print("git_commit_id: ", git_commit_id)

        # Git modified files from commit ID
        cmd = "git diff-tree --no-commit-id --name-only -r {}" \
                    .format(git_commit_id) \
                    .split()
        # print("cmd: ", cmd)

        out = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        stdout,stderr = out.communicate()

        items = stdout.strip().decode("utf8").split("\n")

        for it_item in items:
            base,ext = os.path.splitext(it_item)
            if (ext in options.CPP_MASK):
                result += it_item.strip() + " "

        result = result.strip()

        print("Files: ", result)

        return result

    def isError(self, a_out, a_stderr_str):
        """ Check if errors detected """

        return bool((a_out.returncode == 1 or re.search("^.*(error|warning).*$", a_stderr_str, re.MULTILINE)) and
            a_stderr_str.find("Error while processing") > 0)

    def traceColor(self, a_color, a_msg):
        """ Trace using color """

        if (len(a_msg) == 0):
            return

        print(a_color + self._name + self.COLOR_NORMAL + " " + a_msg)

    def traceOk(self, a_msg):
        """ Trace as OK """

        if (len(a_msg) == 0):
            return

        print(self.COLOR_YELLOW + self._name + self.COLOR_NORMAL + " " +
            self.COLOR_GREEN + a_msg + self.COLOR_NORMAL)

    def traceError(self, a_msg):
        """ Trace as error """

        if (len(a_msg) == 0):
            return

        print(self.COLOR_RED + self._name + " " + a_msg + self.COLOR_NORMAL)
#--------------------------------------------------------------------------------------------------
def main():
    if (options.SKIP_CHECK == "1"):
        sys.exit(0)

    arguments_parser = argparse.ArgumentParser(description='Arguments:')
    arguments_parser.add_argument('--file-to-check', type=str, help='Optional. Full path to file to be checked.')

    try:
        analyzer = Analyzer(options.TYPE_ACTIVE)
        analyzer.traceOptions()
        analyzer.run()
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        print("")

    sys.exit(0)
#--------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
#--------------------------------------------------------------------------------------------------
