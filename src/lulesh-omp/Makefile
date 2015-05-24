LEVEL=../..
PROJECT=lulesh-omp
DOMAIN=scientific

EDGE_ELEMS = 20
include $(LEVEL)/Makefile.common

$(PROFBIN_F): $(RUN_F)
	$(V_RUN)./$^ $(EDGE_ELEMS)
