LEVEL   := ../..
PROJECT := ruby
TESTDIR=$(TESTINPUT)/compilation/ruby
DOMAIN=compilation

include $(LEVEL)/Makefile.common

$(PROFBIN_F): $(RUN_F)
	$(V_RUN)env RUBYOPT="" ruby $(TESTDIR)/benchmark/run.rb \
	  --ruby="$<" \
	  --opts="-I$(TESTDIR)/lib -I$(TESTDIR)/. -I$(TESTDIR)/.ext/common" -r
