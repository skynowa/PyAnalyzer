#!/usr/bin/env python

#--------------------------------------------------------------------------------------------------
# \file  git_client.py
# \brief Git client
#--------------------------------------------------------------------------------------------------


import os
import subprocess

from distutils import spawn

import trace
#--------------------------------------------------------------------------------------------------
class GitClient:
	""" Git client """

	def __init__(self):
		self.trace = trace.Trace(self.__class__.__name__)

	def execName(self):
		return "git"

	def checkValid(self):
		""" Validate """

		# Executable
		execPath = spawn.find_executable( self.execName() )
		if (execPath is None):
			self.trace.error("{} - not installed".format( self.execName() ))
			exit(1)

	def filesFromCommit(self, a_cppMask, a_commitId):
		""" Get modified files from commit ID """
		result = []

		cmd = [self.execName(), "diff-tree", "--no-commit-id", "--name-only", "-r", a_commitId]
		self.trace.info("[cmd] {}".format(cmd))

		proc   = None
		stdOut = ""
		stdErr = ""

		try:
			proc = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
			stdOut, stdErr = proc.communicate()
			if (proc.returncode != 0):
				self.trace.error("Proc error: {} - {}".format(proc.returncode, stdErr))
		except subprocess.CalledProcessError as a_error:
			self.trace.error("Exception: {} - {}".format(a_error.returncode, a_error.output))

		files = stdOut.strip().decode("utf8").split("\n")

		for it_file in files:
			base, ext = os.path.splitext(it_file)
			if (ext in a_cppMask):
				result.append( it_file.strip() )

		self.trace.ok("Files: {}".format(result))

		return result

	def filesFromHead(self, a_cppMask):
		""" Get modified files from HEAD commit """

		result = []

		# Git commit ID
		cmd = [self.execName(), "log", "--format='%H'", "-n 1"]
		self.trace.info("[cmd] {}".format(cmd))

		proc   = None
		stdOut = ""
		stdErr = ""

		try:
			proc = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
			stdOut, stdErr = proc.communicate()
			if (proc.returncode != 0 and
				proc.returncode != 128
			):
				self.trace.error("Proc error: {} - {}".format(proc.returncode, stdErr))
		except subprocess.CalledProcessError as a_error:
			self.trace.error("Exception: {} - {}".format(a_error.returncode, a_error.output))

		commitId = stdOut.strip().decode("utf8").replace("'", "")
		# self.trace.ok("commitId: {}".format(commitId))

		result = self.filesFromCommit(a_cppMask, commitId)

		return result
#--------------------------------------------------------------------------------------------------
