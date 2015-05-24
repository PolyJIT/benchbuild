PROJECT=xlintstrfz
COMPILER = gfortran
LAPACK=..
DOMAIN=scientific
LEVEL=../../..

include $(LAPACK)/Makefile.lapack

$(PROFBIN_F): $(RUN_F)
	$(V)echo Testing COMPLEX16 LAPACK RFP protoype linear equation routines
	$^ < $(TESTDIR)/ztest_rfp.in 2>&1

