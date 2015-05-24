LEVEL=../..
PROJECT=crafty
DOMAIN=scientific
TESTDIR=$(TESTINPUT)/$(DOMAIN)/$(PROJECT)
include $(LEVEL)/Makefile.common

$(PROFBIN_F): profbin_f=$(subst %,$*,$(PROFBIN_F))
$(PROFBIN_F): $(RUN_F)
	$(VERB)(cat $(TESTDIR)/test1.sh | $^)
	$(VERB)(cat $(TESTDIR)/test2.sh | $^)
