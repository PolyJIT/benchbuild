LEVEL=../..
PROJECT=python
TESTDIR=${TESTINPUT}/compilation/$(PROJECT)
DOMAIN=compilation

PYTHONPATH=$(TESTDIR)
PYTHONHOME=$(TESTDIR)

include $(LEVEL)/Makefile.common

$(PROFBIN_F): $(RUN_F)
	for f in `find $(TESTDIR) -iname "*.py" | head -n 10`; do \
	  $(V_RUN)env PYTHONPATH="$(PYTHONPATH)" PYTHONHOME="$(PYTHONHOME)" $< $$f; \
	done;
