PROJECT=xlintstrfc
COMPILER = gfortran
LAPACK=..
DOMAIN=scientific
LEVEL=../../..

include $(LAPACK)/Makefile.lapack

$(PROFBIN_F): $(RUN_F)
	@echo Testing COMPLEX LAPACK RFP protoype linear equation routines
	$^ < $(TESTDIR)/ctest_rfp.in 2>&1

