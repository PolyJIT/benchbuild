# Extend the DIRS variable if you want make to setup new
# folders for you. This will create the missing directories
# and link the latex/Makefile.
#
DIRS = src\
       polybench

LEVEL = .

include $(LEVEL)/Makefile.common
