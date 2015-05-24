PROJECT=xlintstc
COMPILER = gfortran
LAPACK=..
DOMAIN=scientific
LEVEL=../../..

include $(LAPACK)/Makefile.lapack

$(PROFBIN_F): $(RUN_F)
	$(V)echo Testing COMPLEX LAPACK linear equation routines
	$^ < $(TESTDIR)/ctest.in 2>&1

