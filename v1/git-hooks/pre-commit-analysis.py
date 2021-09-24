#!/usr/bin/env python

#--------------------------------------------------------------------------------------------------
# \file  pre-commit-analysis.py
# \brief Run static code analysis for modified C++ files
#
# https://clang.llvm.org/extra/clang-tidy/
# http://cppcheck.sourceforge.net/
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
        self.PROJECT_DIR = "/home/httpd/triptake-all"

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
        self._git_modified_files = self.getGitModifiedFiles()
        if (len(self._git_modified_files) == 0 and self._type != options.TYPE_CLANG_TIDY_FILE):
            self.traceOk("No changes. OK")
            sys.exit(0)

        """ compiler info """
        self._complier_id, self._complier_name = self.getComplierInfo()

        """ C++ include dirs """
        self._include_dirs = self.getIncludeDirs()

        """ file to check for manual run """
        self._file_to_check = ""


    def run(self):
        """ Run analysis by type """

        if (options.QUICK_CHECK == 1):
            self.traceOk("Start analysis (quick)...")
        else:
            self.traceOk("Start analysis (full)...")

        out = None

        # profiler
        time_start_sec = time.time()

        if   (self._type == options.TYPE_CPPCHECK):
            out = self.runCppcheck()
        elif (self._type == options.TYPE_CLANG_TIDY):
            out = self.runClangTidy()
        elif (self._type == options.TYPE_CLANG_TIDY_DIFF):
            out = self.runClangTidyDiff()
        elif (self._type == options.TYPE_CLANG_TIDY_FILE):
            out = self.runClangTidyFile()

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
        print("COMPILER_ID: ", self._complier_name)
        print("QUICK_CHECK: ", options.QUICK_CHECK)
        print("SKIP_CHECK:  ", options.SKIP_CHECK)
        print("STOP_ON_FAIL:", options.STOP_ON_FAIL)
        print("CPP_STD:     ", options.CPP_STD)
        print("CPP_MASK:    ", ", ".join(options.CPP_MASK))
        print("")

    """ private """
    def runCppcheck(self):
        """ Run analysis Cppcheck """

        cmd = \
            "cppcheck " \
            "{} {} " \
            "--library=std.cfg --library=posix.cfg " \
            "-UKERN_PROC_PATHNAME " \
            "--enable={} --inconclusive " \
            "--language=c --language={} --std={} " \
            "--platform=unix64 " \
            "--force " \
            "-j{} " \
            "--relative-paths " \
            "--error-exitcode=1" \
            .format(self._include_dirs, self._git_modified_files, options.CPPCHECK_ERROR_LEVEL,
                options.CPP_LANG, options.CPP_STD, self.JOBS_NUM) \
            .split()
        print("cmd: ", cmd)

        return subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)

    def runClangTidy(self):
        """ Run analysis by Clang-Tidy """

        line_filter = "" # n/a

        args_stdlib = {
            self.COMPILER_ID_CLANG: "-stdlib=libstdc++",
            self.COMPILER_ID_GCC:   ""
        }

        force_cpp = "-x " + options.CPP_LANG

        header_filter = ""
        if (options.QUICK_CHECK == 1):
            header_filter = "" # skip
        else:
            header_filter = "^{}/.*".format(self.PROJECT_DIR) # all

        cmd = \
            "clang-tidy " \
            "{} " \
            "-system-headers=0 " \
            "-line-filter={} " \
            "-header-filter={} " \
            "-extra-arg=-std={} " \
            "-extra-arg={} " \
            "-quiet " \
            "-- " \
            "{} " \
            "{}" \
            .format(self._git_modified_files, line_filter, header_filter,
                options.CPP_STD, args_stdlib[self._complier_id], self._include_dirs,
                force_cpp) \
            .split()
        print("cmd: ", cmd)

        return subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)

    def runClangTidyDiff(self):
        """ Run analysis by Clang-Tidy-Diff """

        line_filter = self.getGitModifiedFilesLineFilter()

        args_stdlib = {
            self.COMPILER_ID_CLANG: "-stdlib=libstdc++",
            self.COMPILER_ID_GCC:   ""
        }

        force_cpp = "-x " + options.CPP_LANG

        header_filter = ""
        if (options.QUICK_CHECK == 1):
            header_filter = "" # skip
        else:
            header_filter = "^{}/.*".format(self.PROJECT_DIR) # all

        cmd = \
            "clang-tidy " \
            "{} " \
            "-system-headers=0 " \
            "-line-filter={} " \
            "-header-filter={} " \
            "-extra-arg=-std={} " \
            "-extra-arg={} " \
            "-quiet " \
            "-- " \
            "{} " \
            "{}" \
            .format(self._git_modified_files, line_filter, header_filter,
                options.CPP_STD, args_stdlib[self._complier_id], self._include_dirs,
                force_cpp) \
            .split()
        print("cmd: ", cmd)

        return subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)

    def runClangTidyFile(self):
        """ Run analysis by Clang-Tidy-File """

        args_stdlib = {
            self.COMPILER_ID_CLANG: "-stdlib=libstdc++",
            self.COMPILER_ID_GCC:   ""
        }

        force_cpp = "-x " + options.CPP_LANG

        header_filter = ""
        if (options.QUICK_CHECK == 1):
            header_filter = "" # skip
        else:
            header_filter = "^{}/.*".format(self.PROJECT_DIR) # all

        cmd = \
            "clang-tidy " \
            "{} " \
            "-system-headers=0 " \
            "-header-filter={} " \
            "-extra-arg=-std={} " \
            "-extra-arg={} " \
            "-quiet " \
            "-- " \
            "{} " \
            "{}" \
            .format(self._file_to_check, header_filter,
                options.CPP_STD, args_stdlib[self._complier_id], self._include_dirs,
                force_cpp) \
            .split()
        print("cmd: ", cmd)

        return subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)


    def getComplierInfo(self):
        """ Get complier info (ID, name) """

        cmd = "c++ --version".split()

        out = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        stdout,stderr = out.communicate()
        if (out.returncode == 1):
            self.traceError("getComplierInfo")
            return self.COMPILER_ID_UNKNOWN

        version_str = stdout.decode("utf8").strip();
        if (version_str.find("clang version") > 0):
            return self.COMPILER_ID_CLANG, "clang"
        else:
            return self.COMPILER_ID_GCC, "gcc"

    def getIncludeDirs(self):
        """ Get include dirs """

        result = ""

        if (options.TYPE_ACTIVE == options.TYPE_CPPCHECK and
            options.QUICK_CHECK == 1
        ):
            result = ""
        else:
            """ System includes (cpp -v) """
            if (1) :
                result = \
                    self.getCompilerIncludeDirs() + " "
            else:
                result = \
                    "-I/usr/lib/gcc/x86_64-linux-gnu/8/include " \
                    "-I/usr/local/include " \
                    "-I/usr/lib/gcc/x86_64-linux-gnu/8/include-fixed " \
                    "-I/usr/include/x86_64-linux-gnu " \
                    "-I/usr/include"

            result += \
                "-I/usr/local/include " + \
                "".join(self.getPkgConfig("libxml-2.0")) + " " + \
                "".join(self.getPkgConfig("ImageMagick")) + " " + \
                \
                "-I/usr/local/gen++v3/class " + \
                "-I" +       self.PROJECT_DIR + "/functions " + \
                "-isystem" + self.PROJECT_DIR + "/suppliers/gen/base " + \
                "-isystem" + self.PROJECT_DIR + "/booked/gen/base " + \
                "-isystem" + self.PROJECT_DIR + "/syntexts/gen/base " + \
                "-isystem" + self.PROJECT_DIR + "/core/gen/base " + \
                "-isystem" + self.PROJECT_DIR + "/api/gen/base " + \
                "-isystem" + self.PROJECT_DIR + "/seo/gen/base"
        return result

    def getCompilerIncludeDirs(self):
        """  Get complier include dirs """

        result = ""

        cmd = "cpp -v /dev/null".split()

        out = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        stdout,stderr = out.communicate()

        out_info = stderr.decode("utf8")

        str_left    = "#include <...> search starts here:"
        str_right   = "End of search list."

        pos_left  = out_info.find(str_left)
        pos_right = out_info.find(str_right, pos_left)
        assert pos_left < pos_right

        includes = out_info[int(pos_left) + len(str_left):int(pos_right)].strip().split()

        for it_include in includes:
            result += "-I" + it_include + " "

        if (self._os_name == "FreeBSD") :
            result += "-isystem/usr/include/c++/v1"

        return result

    def getGitModifiedFiles(self):
        """ Get current GIT modified files """

        result = ""

        cmd_commit_diff = "git diff --name-only --cached --diff-filter=ACM".split()
        cmd_master_diff = "git diff --name-only master".split()

        cmd = cmd_commit_diff

        out = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        stdout,stderr = out.communicate()

        items = stdout.strip().decode("utf8").split("\n")

        for it_item in items:
            base,ext = os.path.splitext(it_item)
            if (ext in options.CPP_MASK):
                result += it_item.strip() + " "

        return result

    def getGitModifiedFilesLineFilter(self):
        """ Get current GIT modified lines line filter (JSON) """

        # strip the smallest prefix containing P slashes
        p      = 1
        iregex = r'.*\.(h|hh|hpp|inl|cc|cpp|cxx)'

        cmd = "git diff -U0 HEAD".split()

        out = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)

        ## result = stderr.strip().decode("utf8")
        # print("stderr: ", result)

        # extract changed lines for each file
        filename      = None
        lines_by_file = {}

        for it_line in iter(out.stdout.readline, ''):
            line = it_line.decode("utf-8")
            if (not line):
                break

            match = re.search('^\+\+\+\ \"?(.*?/){%s}([^ \t\n\"]*)' % p, line)
            if (match):
                filename = match.group(2)

            if (filename == None):
                continue

            if (not re.match('^%s$' % iregex, filename, re.IGNORECASE)):
                continue

            # print("C++ filename: ", filename)

            match = re.search('^@@.*\+(\d+)(,(\d+))?', line)
            if (match):
                start_line = int(match.group(1))
                line_count = 1

                if (match.group(3)):
                    line_count = int(match.group(3))

                if (line_count == 0):
                    continue

                end_line = start_line + line_count - 1;
                lines_by_file.setdefault(filename, []).append([start_line, end_line])
        # for (out.stdout)

        if (len(lines_by_file) == 0):
            print("No diffs")
            sys.exit(0)

        line_filter_json = json.dumps(
            [{"name" : name, "lines" : lines_by_file[name]} for name in lines_by_file],
            separators = (',', ':'))

        return line_filter_json

    def getPkgConfig(self, a_lib_name):
        """ Get libs, cflags by pkg-config tool """

        try:
            # cmd_libs = ["pkg-config", "--libs-only-L",   a_lib_name]
            # libs = (
            #     subprocess.check_output(cmd_libs)
            #     .decode("utf8")
            #     .strip()
            #     # .replace("-L", "")
            # )

            cmd_cflags = ["pkg-config", "--cflags-only-I", a_lib_name]
            cflags = (
                subprocess.check_output(cmd_cflags)
                .decode("utf8")
                .strip()
                .replace("-I", "-isystem") # suppress all warnings
            )

            return (cflags)
        except Exception:
            self.traceError("pkg-config: " + a_lib_name + " - fail")
            pass

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
def main(argv):
    if (options.SKIP_CHECK == "1"):
        sys.exit(0)

    arguments_parser = argparse.ArgumentParser(description='Arguments:')
    arguments_parser.add_argument('--file-to-check', type=str, help='Optional. Full path to file to be checked.')

    try:
        analyzer = Analyzer(options.TYPE_ACTIVE)
        analyzer._file_to_check = arguments_parser.parse_args().file_to_check

        analyzer.traceOptions()
        analyzer.run()
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        print("")

    sys.exit(0)
#--------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    main( sys.argv[1:] )
#--------------------------------------------------------------------------------------------------
