PROJECT=xlintsts
COMPILER = gfortran
LAPACK=..
DOMAIN=scientific
LEVEL=../../..

include $(LAPACK)/Makefile.lapack

$(PROFBIN_F): $(RUN_F)
	$(V)echo Testing REAL LAPACK linear equation routines
	$(V_RUN)$^ < $(TESTDIR)/stest.in 2>&1

