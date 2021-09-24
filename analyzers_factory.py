#!/usr/bin/env python

#--------------------------------------------------------------------------------------------------
# \file  analyzers_factory.py
# \brief SA factory
#--------------------------------------------------------------------------------------------------


import options
import cppcheck
import clang_tidy
#--------------------------------------------------------------------------------------------------
class AnalyzerFactory:
	""" Analyzers factory """

	def createAnalyzer(self, a_type, a_filesSrc):
		""" Create SA by type """

		sa = None

		dirSrc     = options.DIR_SRC
		quickCheck = options.QUICK_CHECK
		skipCheck  = options.SKIP_CHECK
		stopOnFail = options.STOP_ON_FAIL
		cppStd     = options.CPP_STD
		cppMask    = options.CPP_MASK

		if (a_type == options.TYPE_CPPCHECK):
			sa = cppcheck.Cppcheck(a_filesSrc, dirSrc, quickCheck, skipCheck, stopOnFail, cppStd,
					cppMask)
		elif (a_type == options.TYPE_CLANG_TIDY):
			sa = clang_tidy.ClangTidy(a_filesSrc, dirSrc, quickCheck, skipCheck, stopOnFail, cppStd,
					cppMask)
		else:
			assert 0, "Bad a_type: {}".format(a_type)

		return sa
#--------------------------------------------------------------------------------------------------
