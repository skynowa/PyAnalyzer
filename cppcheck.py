#!/usr/bin/env python

#--------------------------------------------------------------------------------------------------
# \file  cppcheck.py
# \brief Cppcheck analyser
#
# https://github.com/danmar/cppcheck
#--------------------------------------------------------------------------------------------------


import re

import analyzer
#--------------------------------------------------------------------------------------------------
class Cppcheck(analyzer.IAnalyzer):
	def __init__(
		self,
		a_filesSrc,
		a_dirSrc,
		a_quickCheck,
		a_skipCheck,
		a_stopOnFail,
		a_cppStd,
		a_cppMask
	):
		super(Cppcheck, self).__init__(a_filesSrc, a_dirSrc, a_quickCheck, a_skipCheck,
			a_stopOnFail, a_cppStd, a_cppMask)

	def checkValid(self):
		super(Cppcheck, self).checkValid()

	def name(self):
		return "Cppcheck"

	def execName(self):
		return "cppcheck"

	def version(self):
		rv = ""

		cmd = [self.execName(), "--version"]

		returnCode, stdOut, stdErr = self._run(cmd)

		match = re.search(r"cppcheck (.+?)$", stdOut, re.IGNORECASE)
		if match:
			rv = match.group(1)

		return rv

	def cfgPath(self):
		return self.dirPath() + "/ErrorLevels.txt"

	def run(self):
		super(Cppcheck, self).run()

		# Result
		self._stdOut = ""
		self._stdErr = ""

		""" Params """

		# srcPath
		srcPath = "{}/{}".format(self.dirSrc, "cppcheck_src.txt")
		self._writeFile(srcPath, self._filesSrc)

		cfgEnable       = self._readConfig( self.cfgPath() ).strip()
		cfgSuppressions = self.dirPath() + "/Suppressions.txt"
		jobsNum         = 1

		# cmd
		cmd = [
			self.execName(),
			# "--project={}".format(self._compileDbPath),
			# "--project={}".format(self._compileDbLightPath),
			"--file-list={}".format(srcPath),
			"--cppcheck-build-dir={}".format(self.dirBuild),
			"--relative-paths",

			"-isystem",
			"-I.{}".format(self.dirSrc),

			"--language=c++",
			"--std={}".format(self.cppStd),
			"--library=std.cfg",
			"--library=posix.cfg",
			"--platform=unix64",

			"--enable={}".format(cfgEnable),
			"--inconclusive",
			"--force",
			"--max-configs=1",

			"--suppress=missingIncludeSystem",
			"--suppressions-list={}".format(cfgSuppressions),

			"--error-exitcode=1",

			"--report-progress",
			"--verbose",
			# "--quiet",

			"--template='{{severity}}|{{id}}|{{message}}|{{file}}|{{line}}:{{column}}|{{callstack}}|{{code}}'",

			"-j{}".format(jobsNum)
		]
		self.trace.info("[cmd] {}".format(cmd))

		# --quiet

		## Report:
		# '{file}:{line},{severity},{id},{message}' or
		# '{file}({line}):({severity}) {message}' or
		# '{callstack} {message}'
		#
		# --output-file=./Report.csv # Write results to file, rather than standard error.
		# --xml             # Write results in xml format to error stream (stderr).
		# --xml-version=2   #

		# Dev params:
		# - --showtime=summary

		self._returnCode, self._stdOut, self._stdErr = self._run(cmd)

	def report(self):
		super(Cppcheck, self).report()

	def _removeExtraWarnings(self, a_str):
		a_str = re.sub(r"\d+ warnings and \d error generated\.", "", a_str).strip()

		return a_str

	def _checkError(self):
		super(Cppcheck, self)._checkError()
#--------------------------------------------------------------------------------------------------
