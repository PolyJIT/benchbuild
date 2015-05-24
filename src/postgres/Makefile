LEVEL=../..
PROJECT=postgres
DOMAIN=database

TESTDIR=$(TESTINPUT)/dbms/$(PROJECT)
TEST_DIR=$(TESTDIR)/test-data

CLIENTS= 10
TRANSACTION= 100000

include $(LEVEL)/Makefile.common

%/$(TIME_F): %/$(PROFBIN_F)
	    $(VERB)mv ./$(TIME_F) $@

%/$(PROJECT)$(CALLS_EXT): %/$(PROFBIN_F)
	    $(VERB)mv $(TEST_DIR)/$(PAPI_CALL_STACK_FILE) $@

%/$(PROJECT)$(PROFILE_EXT): %/$(PROFBIN_F)
	    $(VERB)mv $(TEST_DIR)/$(PROFBIN_F) $@

$(PROFBIN_F): $(RUN_F)
	    $(VERB)ln -sf $^
	    $(VERB)ln -sf $^.bin
	    -$(VERB)$(TESTDIR)/pg_ctl stop -t 360 -w -D $(TESTDIR)/test-data
	    $(VERB)$(TESTDIR)/pg_ctl start -p ./$(PROJECT) -w -D $(TESTDIR)/test-data
	    -$(VERB)$(TESTDIR)/dropdb pgbench
	    $(VERB)$(TESTDIR)/createdb -O simbuerg pgbench
	    $(VERB)$(TESTDIR)/pgbench -i -U simbuerg pgbench
	    $(VERB)$(TESTDIR)/pgbench -c $(CLIENTS) -S -t $(TRANSACTION) -U simbuerg pgbench
	    $(VERB)$(TESTDIR)/dropdb pgbench
	    $(VERB)$(TESTDIR)/pg_ctl stop -t 360 -w -D $(TESTDIR)/test-data
	    $(VERB)rm -f $(PROJECT)
	    $(VERB)rm -f $(BIN_F)

