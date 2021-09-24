ANALYSIS_CPP_STD = c++17

# Sources
ANALYSIS_INCLUDES = \
	-I/usr/include \
	\
	-I/usr/local/include \
	-I/usr/local/include/libxml2 \
	-I/usr/local/include/ImageMagick-6 \
	\
	-I/usr/local/gen++v3/class \
	-I../gen/base \
	-I$(PWD)
ANALYSIS_SOURCE_FILES = *.cc

# defines
# Cppcheck   - n/a (by default checks all preprocessor configurations)
# Clang-tidy -
# ANALYSIS_DEFINES=-DPROJECT_CORE -DPROJECT_BOOKED -DPROJECT_SUPPLIERS -DPROJECT_SECURE

# detect only errors
ANALYSIS_LEVEL_ERROR = 1

# $(info )
# $(info -------------------- ANALYSIS --------------------)
# $(info CPP_STD:      ${ANALYSIS_CPP_STD})
# $(info INCLUDES:     ${ANALYSIS_INCLUDES})
# $(info SOURCE_FILES: ${ANALYSIS_SOURCE_FILES})
# $(info DEFINES:      ${ANALYSIS_DEFINES})
# $(info LEVEL_ERROR:  ${ANALYSIS_LEVEL_ERROR})
# $(info --------------------------------------------------)
# $(info )

include ../../analysis/cppcheck/Makefile.inc
include ../../analysis/clang-tidy/Makefile.inc
