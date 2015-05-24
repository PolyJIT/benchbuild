PROJECT=xlintstds
COMPILER = gfortran
LAPACK=..
DOMAIN=scientific
LEVEL=../../..

include $(LAPACK)/Makefile.lapack

$(PROFBIN_F): $(RUN_F)
	$(V)echo Testing SINGLE-DOUBLE PRECISION LAPACK prototype linear equation routines
	$^  < $(TESTDIR)/dstest.in 2>&1

