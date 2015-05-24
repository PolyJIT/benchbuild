PROJECT=xlintstzc
COMPILER = gfortran
LAPACK=..
DOMAIN=scientific
LEVEL=../../..

include $(LAPACK)/Makefile.lapack

$(PROFBIN_F): $(RUN_F)
	@echo Testing COMPLEX-COMPLEX16 LAPACK protoype linear equation routines
	$^  < $(TESTDIR)/zctest.in 2>&1

