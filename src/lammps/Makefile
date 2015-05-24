LEVEL=../..
PROJECT=lammps
DOMAIN=scientific
TESTDIR=$(TESTINPUT)/$(DOMAIN)/$(PROJECT)
include $(LEVEL)/Makefile.common

$(PROFBIN_F): $(RUN_F)
	for f in `find $(TESTDIR) -iname "in.*"`; do \
	  echo "[Running on: $$f]"; \
	  ./$^ < $$f; \
	done;
