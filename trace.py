#!/usr/bin/env python

#--------------------------------------------------------------------------------------------------
# \file  trace.py
# \brief
#--------------------------------------------------------------------------------------------------


#--------------------------------------------------------------------------------------------------
class Trace:
	""" Trace messages """

	def __init__(self, a_name):
		""" Ctor """
		# Shell colors
		self.COLOR_RED        = "\033[0;91m"
		self.COLOR_YELLOW     = "\033[0;93m"
		self.COLOR_BLUE       = "\033[0;34m"
		self.COLOR_BLUE_LIGHT = "\033[94m"
		self.COLOR_GREEN      = "\033[0;92m"
		self.COLOR_MAGENTA    = "\033[0;95m"
		self.COLOR_CYAN_LIGHT = "\033[0;96m"
		self.COLOR_NORMAL     = "\033[0m"

		self._name = "[{}]".format(a_name)

	def info(self, a_msg):
		""" Trace as OK """

		print(a_msg)

	def debug(self, a_msg):
		""" Trace as OK """

		if (len(a_msg) == 0):
			return

		print(self.COLOR_YELLOW + self._name + self.COLOR_NORMAL + " " +
			self.COLOR_BLUE_LIGHT + a_msg + self.COLOR_NORMAL)

	def ok(self, a_msg):
		""" Trace as OK """

		if (len(a_msg) == 0):
			return

		print(self.COLOR_YELLOW + self._name + self.COLOR_NORMAL + " " +
			self.COLOR_GREEN + a_msg + self.COLOR_NORMAL)

	def report(self, a_msg):
		""" Trace report """

		if (len(a_msg) == 0):
			return

		print(self.COLOR_YELLOW + self._name + self.COLOR_NORMAL + " " +
			self.COLOR_CYAN_LIGHT + a_msg + self.COLOR_NORMAL)

	def error(self, a_msg):
		""" Trace as error """

		if (len(a_msg) == 0):
			return

		print(self.COLOR_RED + self._name + " " + a_msg + self.COLOR_NORMAL)
#--------------------------------------------------------------------------------------------------
