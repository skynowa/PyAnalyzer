#!/usr/bin/env python

#--------------------------------------------------------------------------------------------------
# \file  clang_tidy.py
# \brief Clang-Tidy analyzer
#
# https://clang.llvm.org/extra/clang-tidy/
#--------------------------------------------------------------------------------------------------


import re

import analyzer
#--------------------------------------------------------------------------------------------------
class ClangTidy(analyzer.IAnalyzer):
	def __init__(
		self,
		a_filesSrc,
		a_dirSrc,
		a_quickCheck,
		a_skipCheck,
		a_stopOnFail,
		a_cppStd,
		a_cppMask
	) :
		super(ClangTidy, self).__init__(a_filesSrc, a_dirSrc, a_quickCheck, a_skipCheck,
			a_stopOnFail, a_cppStd, a_cppMask)

	def checkValid(self):
		super(ClangTidy, self).checkValid()

	def name(self):
		return "Clang-Tidy"

	def execName(self):
		return "clang-tidy"

	def version(self):
		rv = ""

		cmd = [self.execName(), "--version"]

		returnCode, stdOut, stdErr = self._run(cmd)

		match = re.search(r"llvm version (.+?)\n", stdOut, re.IGNORECASE)
		if match:
			rv = match.group(1)

		return rv

	def cfgPath(self):
		return self.dirPath() + "/.clang-tidy"

	def run(self):
		super(ClangTidy, self).run()

		# Result
		self._stdOut = ""
		self._stdErr = ""

		""" Params """

		cfgEnable      = "{" + self._readConfig( self.cfgPath() ).strip() + "}"

		system_headers = ""
		header_filter  = ""

		if (self.quickCheck == 1):
			system_headers = "" # skip
			header_filter  = "" # skip
		else:
			system_headers = "1"
			header_filter  = "^{}/.*".format(self.dirSrc) # all

		# cmd
		cmd = []
		cmd.append( self.execName() )

		for it_fileSrc in self._filesSrc:
			cmd.append(it_fileSrc)

		cmd.extend([
			"-p={}".format(self.dirBuild),
			"-config={}".format(cfgEnable),
			"-system-headers={}".format(system_headers),
			"-header-filter={}".format(header_filter),
			"-extra-arg=-std={}".format(self.cppStd)
		])
		self.trace.info("[cmd] {}".format(cmd))

		# -quiet

		self._returnCode, self._stdOut, self._stdErr = self._run(cmd)

	def report(self):
		super(ClangTidy, self).report()

	def _removeExtraWarnings(self, a_str):
		a_str = re.sub(r"\d+ warnings generated\.", "", a_str).strip()
		a_str = re.sub(r"Suppressed \d+ warnings \(\d+ in non-user code\)\.", "", a_str).strip()
		a_str = re.sub(r"Use -header-filter=\.\* to display errors from all non-system headers\. Use -system-headers to display errors from system headers as well\.", "", a_str).strip()

		return a_str

	def _checkError(self):
		super(ClangTidy, self)._checkError()
#--------------------------------------------------------------------------------------------------
