LEVEL=../..
PROJECT=minisat
DOMAIN=verification
TESTDIR=$(TESTINPUT)/$(DOMAIN)/$(PROJECT)
include $(LEVEL)/Makefile.common

$(PROFBIN_F): $(RUN_F)
	-for f in `find $(TESTDIR) -iname "*.cnf.gz" | head -n 1`; do \
	  echo "[Running on: $$f]"; \
	  $< < $$f; \
	done;
