LEVEL   := ../..
PROJECT := sdcc
DOMAIN = compilation

BIN_DIR = src/bin
SRC_DIR = src/src

include $(LEVEL)/Makefile.common

raw/$(PROFBIN_F): raw/$(RUN_F)
	  $(V)cp raw/$^ $(BIN_DIR)
	  $(V)cp raw/$(BIN_F) $(BIN_DIR)
	  $(V)make -C$(SRC_DIR)/regression
	  $(V)make -C$(SRC_DIR)/regression clean
	  $(V)make -i -Csrc/support/tests/dhrystone/
	  $(V)make -Csrc/support/tests/dhrystone/ clean
	  $(V_RM)rm $(BIN_DIR)/$(PROJECT)
	  $(V_RM)rm $(BIN_DIR)/$(BIN_F)

%/$(CALLS_F): %/$(PROFBIN_F)
	  $(V)cat ./src/support/tests/dhrystone/$(PAPI_CALL_STACK_FILE) \
	      ./src/src/regression/$(PAPI_CALL_STACK_FILE) >> $@
	  $(V_RM)rm -f ./src/support/tests/dhrystone/$(PAPI_CALL_STACK_FILE)
	  $(V_RM)rm -f ./src/src/regression/$(PAPI_CALL_STACK_FILE)

%/$(TIME_F): %/$(PROFBIN_F)
	  $(V_MV)mv ./$(BIN_DIR)/$(TIME_F) $@

%/$(PROFBIN_F): %/$(RUN_F)
	  $(V)cp $^ $(BIN_DIR)
	  $(V)cp $^.bin $(BIN_DIR)
	  $(V)make -C$(SRC_DIR)/regression
	  $(V)make -C$(SRC_DIR)/regression clean
	  $(V)make -i -Csrc/support/tests/dhrystone/
	  $(V)make -Csrc/support/tests/dhrystone/ clean
	  $(V_RM)rm $(BIN_DIR)/$(PROJECT)
	  $(V_RM)rm $(BIN_DIR)/$(BIN_F)
	  $(V_MV)mv $(BIN_DIR)/$(BIN_F).profile.out $@
