PROJECT=xlintstrfs
COMPILER = gfortran
LAPACK=..
DOMAIN=scientific
LEVEL=../../..

include $(LAPACK)/Makefile.lapack

$(PROFBIN_F): $(RUN_F)
	$(V)echo Testing REAL LAPACK RFP protoype linear equation routines
	$^ < $(TESTDIR)/stest_rfp.in 2>&1

