LEVEL=../..
PROJECT=linpack
DOMAIN=scientific

include $(LEVEL)/Makefile.common

$(CALLS_F): $(PROJECT)-%-calls

$(PROFBIN_F): calls_f=$(abspath $(subst %,$*,$(CALLS_F)))
$(PROFBIN_F): profbin_f=$(abspath $(subst %,$*,$(PROFBIN_F)))
$(PROFBIN_F): $(RUN_F)
	  $(V_RUN)./$^
	  $(V_MV)mv papi.calls.out $(calls_f)
	  $(V_MV)mv papi$(PROFILE_EXT) $@
