#--------------------------------------------------------------------------------------------------
# \file  Makefile.inc
# \brief clang-tidy makefile target
#
# https://clang.llvm.org/extra/clang-tidy/
# Disable warning in C++ code - use commet: // NOLINT
#--------------------------------------------------------------------------------------------------


CLANG_TIDY_PATH                 = clang-tidy

ifeq (${ANALYSIS_LEVEL_ERROR}, 1)
	CLANG_TIDY_SUPPRESSIONS_FILE = "../../analysis/clang-tidy/Suppressions_errors.txt"
else
	CLANG_TIDY_SUPPRESSIONS_FILE = "../../analysis/clang-tidy/Suppressions.txt"
endif
CLANG_TIDY_SUPPRESSIONS_STR     = '$(shell cat ${CLANG_TIDY_SUPPRESSIONS_FILE} | tr '\n' ',')'

CLANG_TIDY_EXCLUDES_FILE        = "../../analysis/clang-tidy/Excludes.json"
CLANG_TIDY_EXCLUDES             = '$(shell cat ${CLANG_TIDY_EXCLUDES_FILE} | tr -d '\040\011\012\015')'

CLANG_TIDY_REPORT_FILE          = "report.clang-tidy.yaml"


.PHONY: clang-tidy
clang-tidy:
	@echo [clang-tidy] Running ...
	${CLANG_TIDY_PATH} \
	-config='' \
	-export-fixes=${CLANG_TIDY_REPORT_FILE} \
	-header-filter='.*' \
	-line-filter=${CLANG_TIDY_EXCLUDES} \
	-checks=${CLANG_TIDY_SUPPRESSIONS_STR} \
	-system-headers=0 \
	-p=$(PWD) \
	$(PWD)/${ANALYSIS_SOURCE_FILES} \
	-- \
	-std=${ANALYSIS_CPP_STD} \
	${ANALYSIS_INCLUDES} ${ANALYSIS_DEFINES} ${CXXFLAGS}
	# -quiet - n/a (this key doesn't generate a report)
