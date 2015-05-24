PROJECT=xlintstrfd
COMPILER = gfortran
LAPACK=..
DOMAIN=scientific
LEVEL=../../..

include $(LAPACK)/Makefile.lapack

$(PROFBIN_F): $(RUN_F)
	$(V)echo Testing DOUBLE PRECISION LAPACK RFP protoype linear equation routines
	$^ < $(TESTDIR)/dtest_rfp.in 2>&1

