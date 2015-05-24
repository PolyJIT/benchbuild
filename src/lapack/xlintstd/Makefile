PROJECT=xlintstd
COMPILER = gfortran
LAPACK=..
DOMAIN=scientific
LEVEL=../../..

include $(LAPACK)/Makefile.lapack

$(PROFBIN_F): $(RUN_F)
	@echo Testing DOUBLE PRECISION LAPACK linear equation routines
	$^ < $(TESTDIR)/dtest.in 2>&1

