LEVEL   := ../..
PROJECT := js
TESTDIR=$(TESTINPUT)/compilation/spidermonkey
DOMAIN = compilation

include $(LEVEL)/Makefile.common

$(PROFBIN_F): $(RUN_F)
	#./tests/jstests.py ./$^
	$(V_RUN)for f in `find $(TESTDIR)/sunspider -iname "*.js"`; do \
	  echo "[Running on: $$f]"; \
	  $< < $$f; \
	done;
