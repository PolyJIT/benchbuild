# The polli experiment expects the binary to be called: ${PROG}.bin
# As long as there is no easy way to communicate the real program name, we have
# to hardcode it.
#
# Usage:
# 	make EXPERIMENT=polyjit [VERBOSE=1] {raw|std|jit|ext}
#
# This runs:
# 	1. Preoptimization (You can control the flags
# 	2. Optimization per variant {raw|std|jit|ext}
# 	3. Run polli on the optimized IR, without recompilation. This executes
# 	   the IR inside the JIT. You can customize polli's behavior in the
# 	   ./polli.test.sh

#OPT_FLAGS=  -mem2reg -early-cse -functionattrs -instcombine -globalopt -sroa
#OPT_FLAGS+= -gvn -ipsccp -basicaa -simplifycfg -jump-threading -polly-indvars
#OPT_FLAGS+= -loop-unroll -globaldce -polly-prepare
OPT_FLAGS= -polly-canonicalize

# This experiment wants instrumentation
# ${POLLI_FLAGS} is added to all variants

# Bypass preopt/opt & instrumentation stage in this experiment.
$(OPT_F): $(PROJECT).bc
	$(V_OPT)cp $^ $@

# We run with polli, no real asm file needed.
$(BIN_F)-$(EXPERIMENT): $(OPT_F)
	$(V_CP)cp $^ $@

# We want the likwid-csv file in the output dir
$(OUTDIR)/$(PROJECT).$(EXPERIMENT).%.likwid: $(CSV_F)
	$(VERB)cp $^ $@

#$(OUTDIR)/$(PROJECT).$(EXPERIMENT).raw: $(OUTDIR)/.mkdir raw/$(TIME_F)
#	$(VERB)echo "---------------------------------------------------------------" >> $@
#	$(VERB)echo ">>> ========= '$(PROJECT).opt' Program" >> $@
#	$(VERB)echo "---------------------------------------------------------------" >> $@
#	$(V_AWK)awk -F "," '{user+=$$1; sys+=$$2; wall+=$$3} END{ \
#	  print "User time - " user; \
#	  print "System time - " sys; \
#	  print "Wall clock - " wall}' raw/$(TIME_F) >> $@

$(OUTDIR)/$(PROJECT).$(EXPERIMENT).%: time_f=$(abspath $(subst %,$*,$(TIME_F)))
$(OUTDIR)/$(PROJECT).$(EXPERIMENT).%: $(PROFILE_F) $(TIME_F) $(CSV_F) | \
  $(OUTDIR)/.mkdir
	$(VERB)echo "---------------------------------------------------------------" >> $@
	$(VERB)echo ">>> ========= '$(PROJECT).opt' Program" >> $@
	$(VERB)echo "---------------------------------------------------------------" >> $@
	$(VERB)$(PPROF) $< 2>&1 | tee -a $@
	$(V_AWK)awk -F "," '{user+=$$1; sys+=$$2; wall+=$$3} END{ \
	  print "User time - " user; \
	  print "System time - " sys; \
	  print "Wall clock - " wall}' $(time_f) >> $@
