LEVEL=../..
PROJECT=crocopat
DOMAIN=verification
TESTDIR=$(TESTINPUT)/$(DOMAIN)/$(PROJECT)

include $(LEVEL)/Makefile.common

$(PROFBIN_F): $(RUN_F)
	for pat in `find $(TESTDIR)/programs/ -iname "*.rml" | head -n 10`; do \
	  for proj in `find $(TESTDIR)/projects/ -iname "*.rsf"`; do \
	    echo "[Running on: ($$pat, $$proj)]"; \
	    ./$^ $$pat < $$proj; \
	  done; \
	done;
