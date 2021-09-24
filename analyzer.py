#!/usr/bin/env python

#--------------------------------------------------------------------------------------------------
# \file  analyzer.py
# \brief SA base class
#
# https://github.com/skynowa/PyAnalyzer
#--------------------------------------------------------------------------------------------------


import sys
import os
import subprocess
import re
import json
import time
import abc

from distutils import spawn

import trace
#--------------------------------------------------------------------------------------------------
class IAnalyzer(object):
	__metaclass__ = abc.ABCMeta

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
		""" Options """
		self.skipCheck = a_skipCheck
		if (self.skipCheck == 1):
			sys.exit(0)

		self.dirSrc     = a_dirSrc
		self.dirBuild   = "{}_build".format(self.dirSrc)
		self.quickCheck = a_quickCheck
		self.stopOnFail = a_stopOnFail
		self.cppStd     = a_cppStd
		self.cppMask    = a_cppMask

		""" Constants """
		self.isDevel       = True
		self.scriptDirPath = os.path.dirname(__file__)
		self.optionsPath   = "{}/options.py".format(self.scriptDirPath)

		""" Members """
		self.trace     = trace.Trace( self.name() )
		self._filesSrc = a_filesSrc

		# Profiler
		self._timeStartSec = 0.0

		# Result
		self._returnCode = 0
		self._stdOut     = ""
		self._stdErr     = ""

		self._compileDbPath      = "{}/compile_commands.json".format(self.dirBuild)
		self._compileDbLightPath = self._transformCompileDb(self._compileDbPath, self._filesSrc)

	@abc.abstractmethod
	def checkValid(self):
		if (not os.path.exists(self.optionsPath)):
			self.trace.error("{} - not exists".format(self.optionsPath))
			exit(1)

		# SA - executables
		execPath = spawn.find_executable( self.execName() )
		if (execPath is None):
			self.trace.error("{} - not installed".format( self.execName() ))
			exit(1)

		# TODO: [skynowa] SA - versions

		# Source files
		if (len(self._filesSrc) == 0):
			self.trace.ok("No source files. OK")
			sys.exit(0)

		self.trace.ok("Checks. OK")

		# TODO: [skynowa] configs

	@abc.abstractmethod
	def name(self):
		pass

	@abc.abstractmethod
	def execName(self):
		pass

	@abc.abstractmethod
	def version(self):
		pass

	@abc.abstractmethod
	def cfgPath(self):
		pass

	@abc.abstractmethod
	def run(self):
		# Profiler
		self._timeStartSec = time.time()

		if (self.quickCheck == 1):
			self.trace.ok("Start analysis (quick)...")
		else:
			self.trace.ok("Start analysis (full)...")

	@abc.abstractmethod
	def report(self):
		self.trace.report(self._stdOut)
		# self.trace.report(self._stdErr)

		# rm extra warnings
		self._stdErr = self._removeExtraWarnings(self._stdErr)
		self.trace.error(self._stdErr)

		# Profiler
		_timeStopSec = time.strftime("%H:%M:%S", time.gmtime(time.time() - self._timeStartSec))
		self.trace.ok("Finished: {}".format(_timeStopSec))

		self._checkError()

	""" Private """

	@abc.abstractmethod
	def _removeExtraWarnings(self, a_str):
		pass

	@abc.abstractmethod
	def _checkError(self):
		if (self._returnCode == 0 and
			re.search(r"^.*(error|warning).*$", self._stdOut, re.MULTILINE) is None
		):
			self.trace.ok("No errors. OK")
			return

		# Error
		if (self.stopOnFail == 1):
			self.trace.error("***** Detect errors. Exit. *****")
			sys.exit(1)
		else:
			self.trace.error("***** Detect errors. Continue. *****")

	def traceOptions(self):
		""" Trace options """

		self.trace.info("")
		self.trace.ok("Options:")
		self.trace.info("Type:         {} {}".format(self.name(), self.version()))
		self.trace.info("Quick Check:  {}".format(self.quickCheck))
		self.trace.info("Skip Check:   {}".format(self.skipCheck))
		self.trace.info("Stop On Fail: {}".format(self.stopOnFail))
		self.trace.info("Cpp Std:      {}".format(self.cppStd))
		self.trace.info("Cpp Mask:     {}".format(", ".join(self.cppMask)))
		self.trace.info("Current Dir:  {}".format(os.getcwd()))
		self.trace.info("Dir Src:      {}".format(self.dirSrc))
		self.trace.info("Dir Build:    {}".format(self.dirBuild))
		self.trace.info("")

	""" Utils """

	def dirPath(self):
		return "{}/{}".format(self.scriptDirPath, self.execName())

	def _readConfig(self, a_filePath):
		""" Read text config file with comments """

		if (not os.path.exists(a_filePath)):
			self.trace.error("{} - not exists".format(a_filePath))
			return ""

		fileContent = ""

		with open(a_filePath, "r") as file:
			for it_line in file:
				lineFixed = it_line.lstrip(" \t\r\n")

				commentStrs = ["//", "/*", "*", "#", ";", "---", "..."]

				isComment = False

				for it_str in commentStrs:
					if ( lineFixed.startswith(it_str) ):
						# self.trace.info("comment: " + it_line.strip())
						isComment = True
						break

				if (isComment):
					continue

				fileContent += it_line

		return fileContent

	def _writeFileContent(self, a_filePath, a_content):
		""" Write content to text file """

		with open(a_filePath, "w") as file:
			file.write(a_content)
			file.close()

	def _writeFile(self, a_filePath, a_lines):
		""" Write lines to text file """

		with open(a_filePath, "w") as file:
			for it_line in a_lines:
				file.write(it_line + os.linesep)

			file.close()

		if (False and self.isDevel):
			with open(a_filePath, "r") as file:
				self.trace.debug("a_filePath: " + a_filePath)

				for it_line in file.readlines():
					self.trace.debug("  - " + it_line.rstrip())

	def _transformCompileDb(self, a_compileDbPath, a_filesSrc):
		""" Compile DB - transform to the light format """

		# Filter only source files (a_filesSrc)
		compileDbLightPath = []

		# Load JSON file
		jsonFile = open(a_compileDbPath)
		compileDb = json.load(jsonFile)
		jsonFile.close()

		# Parse
		itemsDict = {}

		for it_item in compileDb:
			file = it_item["file"]

			for it_fileSrc in a_filesSrc:
				if (file.find(it_fileSrc) == -1):
					continue

				self.trace.debug("[Compile DB] " + file)

				itemsDict[it_fileSrc] = it_item
		# for

		jsonLight = json.dumps( itemsDict.values() )

		compileDbLightPath = a_compileDbPath #.replace(".json", "_light.json")
		self._writeFileContent(compileDbLightPath, jsonLight)

		self.trace.debug("[Compile Db Light] " + "len = {}".format(len(itemsDict.values())))
		self.trace.debug("[Compile Db Light] " + self._readConfig(compileDbLightPath))

		return compileDbLightPath

	def _run(self, a_cmd):
		""" Run process """

		stdOut = ""
		stdErr = ""

		proc   = None

		try:
			proc = subprocess.Popen(a_cmd, shell = False, bufsize = 0, stdout = subprocess.PIPE,
				stderr = subprocess.PIPE)

			stdOut, stdErr = proc.communicate()
			if (proc.returncode != 0 and
				proc.returncode != 1
			):
				self.trace.error("Proc error: {}".format(proc.returncode))

			stdOut = stdOut.decode("utf8").strip()
			stdErr = stdErr.decode("utf8").strip()
		except subprocess.CalledProcessError as a_error:
			self.trace.error("Exception: {} - {}".format(a_error.returncode, a_error.output))

		return proc.returncode, stdOut, stdErr
#--------------------------------------------------------------------------------------------------
