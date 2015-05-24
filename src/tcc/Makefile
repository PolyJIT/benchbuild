LEVEL   := ../..
PROJECT := tcc
TESTDIR=$(TESTINPUT)/compilation/$(PROJECT)
DOMAIN = compilation

include $(LEVEL)/Makefile.common

#raw/$(PROFBIN_F): raw/$(RUN_F)
#	  $(V)cp -ar $< $(TESTDIR)/$(PROJECT)
#	  $(V)cp -ar raw/$(PROJECT)$(BIN_EXT) $(TESTDIR)/$(PROJECT)$(BIN_EXT)
#	  $(V)make -i -C$(TESTDIR)/ test
#	  $(V_RM)rm $(TESTDIR)/$(PROJECT)
#	  $(V_RM)rm $(TESTDIR)/$(PROJECT)$(BIN_EXT)
#	  $(V)cat $(TESTDIR)/tests/$(PAPI_CALL_STACK_FILE) \
#	  $(V)    $(TESTDIR)/tests2/$(PAPI_CALL_STACK_FILE) >> $@
#	  $(V_RM)rm -f $(TESTDIR)/tests/$(PAPI_CALL_STACK_FILE)
#	  $(V_RM)rm -f $(TESTDIR)/tests2/$(PAPI_CALL_STACK_FILE)

$(CALLS_F): $(PROFBIN_F)
	  $(V)cat $(TESTDIR)/tests/$(PAPI_CALL_STACK_FILE) \
		  $(TESTDIR)/tests2/$(PAPI_CALL_STACK_FILE) >> $@
	  $(V_RM)rm -f $(TESTDIR)/tests/$(PAPI_CALL_STACK_FILE)
	  $(V_RM)rm -f $(TESTDIR)/tests2/$(PAPI_CALL_STACK_FILE)

$(PROFBIN_F): $(RUN_F)
	  $(V)cp -ar $< $(TESTDIR)/$(PROJECT)
	  $(V)cp -ar $*/$(PROJECT_OUTDIR)/$(PROJECT)$(BIN_EXT) $(TESTDIR)/$(PROJECT)$(BIN_EXT)
	  $(V)make -i -C$(TESTDIR)/ test
	  $(V_RM)rm $(TESTDIR)/$(PROJECT)
	  $(V_RM)rm $(TESTDIR)/$(PROJECT)$(BIN_EXT)
	  $(V_MV)mv $(TESTDIR)/$(PROFBIN_F) $@
