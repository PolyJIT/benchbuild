PROJECT=xlintstz
COMPILER = gfortran
LAPACK=..
LEVEL=../../..
DOMAIN=scientific
include $(LAPACK)/Makefile.lapack

$(PROFBIN_F): $(RUN_F)
	$(V)echo Testing COMPLEX16 LAPACK linear equation routines
	$^ < $(TESTDIR)/ztest.in 2>&1

