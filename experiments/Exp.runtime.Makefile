# Bypass preopt/opt & instrumentation stage in this experiment
$(OPT_F): $(PROJECT).bc
	$(V_OPT)/usr/bin/timeout -s KILL 600 opt -load $(POLLY) -polly-canonicalize $(OPT_FLAGS) $(VARIANT_$*) -stats -O3 -o $@ $^

# Dependency is only valid for raw execution class. We do not want to instrument
# yet.
$(BIN_F)-$(EXPERIMENT): $(OPT_F)
	$(V_CLANG)clang -B$(LINKER_DIR) -flto -march=native -O3 $^ -o $@

# We want the likwid-csv file in the output dir
$(OUTDIR)/$(PROJECT).$(EXPERIMENT).%.likwid: $(CSV_F)
	$(VERB)cp $^ $@

$(OUTDIR)/$(PROJECT).$(EXPERIMENT).%: $(TIME_F) | $(OUTDIR)/.mkdir
	$(VERB)echo "---------------------------------------------------------------" >> $@
	$(VERB)echo ">>> ========= '$(PROJECT).opt' Program" >> $@
	$(VERB)echo "---------------------------------------------------------------" >> $@
	$(V_AWK)awk -F "," '{lines+=1; user+=$$1; sys+=$$2; wall+=$$3; mem+=$$4; ctxf+=$$5; ctxv+=$$6; } \
	  END{ print "User time - " user/lines ; \
	       print "System time - " sys/lines ; \
	       print "Wall clock - " wall/lines ; \
	       print "Memory consumption - " mem/lines ; \
	       print "Context switches forced - " ctxf/lines ; \
	       print "Context switches voluntarily - " ctxv/lines ;}' \
	       $*/$(TIME_F) >> $@
