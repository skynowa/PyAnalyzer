#--------------------------------------------------------------------------------------------------
# \file  Makefile.inc
# \brief Cppcheck makefile target
#
# http://cppcheck.sourceforge.net/
#--------------------------------------------------------------------------------------------------


CPPCHECK_PATH              = cppcheck
CPPCHECK_SUPPRESSIONS_FILE = "../../analysis/cppcheck/Suppressions.txt"
CPPCHECK_REPORT_FILE       = "report.cppcheck.csv"
CPPCHECK_REPORT_HEADER     = "severity,id,file,line,callstack,message,inconclusive,code"
CPPCHECK_REPORT_FORMAT     = "\"{severity}\",\"{id}\",\"{file}\",\"{line}\",\"{callstack}\",\"{message}\",\"{inconclusive:inconclusive}\",\"{code}\""

ifeq (${ANALYSIS_LEVEL_ERROR}, 1)
	CPPCHECK_LEVELS = warning
else
	CPPCHECK_LEVELS = warning,performance,portability,information,missingInclude
endif


.PHONY: cppcheck
cppcheck:
	@echo [cppcheck] Running ...
	$(shell echo ${CPPCHECK_REPORT_HEADER} > ${CPPCHECK_REPORT_FILE}) \
	${CPPCHECK_PATH} \
	${ANALYSIS_INCLUDES} $(PWD)/${ANALYSIS_SOURCE_FILES} \
	--library=std.cfg --library=posix.cfg \
	--enable=${CPPCHECK_LEVELS} --inconclusive \
	--language=c++ --std=${ANALYSIS_CPP_STD} \
	--platform=unix64 \
	--template=${CPPCHECK_REPORT_FORMAT} \
	--suppressions-list=${CPPCHECK_SUPPRESSIONS_FILE} \
	--force \
	--quiet \
	-j$(JOBS_NUM) \
	--report-progress \
	--relative-paths \
	2>> ${CPPCHECK_REPORT_FILE}
