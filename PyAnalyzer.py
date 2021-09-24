#!/usr/bin/env python

#--------------------------------------------------------------------------------------------------
# \file  PyAnalyzer.py
# \brief Run static code analysis
#--------------------------------------------------------------------------------------------------


import options
import git_client
import analyzers_factory
#--------------------------------------------------------------------------------------------------
if (__name__ == "__main__"):
	# Files
	git = git_client.GitClient()
	git.checkValid()

	# TODO: [skynowa] prod
	if   (False):
		filesSrc = git.filesFromHead(options.CPP_MASK)
	elif (False):
		filesSrc = [
			"services/sync/dotw_services_sync.cc",
			"services/sync/hotel_beds_v1_services_sync.cc"
		]
	else:
		filesSrc = git.filesFromCommit(options.CPP_MASK, "809628419")

	# SA
	saFact = analyzers_factory.AnalyzerFactory()

	sa = saFact.createAnalyzer(options.TYPE_ACTIVE, filesSrc)
	sa.checkValid()
	sa.traceOptions()
	sa.run()
	sa.report()
#--------------------------------------------------------------------------------------------------
