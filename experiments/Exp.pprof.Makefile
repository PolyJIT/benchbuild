%/$(PROJECT).inst: $(PROJECT).preopt $(LEVEL)/libpprof/libpprof.so
	$(VERB)opt -strip-debug $< -o $@
	$(VERB)polli $(VARIANT_$*) -instrument -no-execution -no-recompilation -stats -o $@ $@ 2>&1 | tee -a $*/$(PROJECT).polli

# Raw has no instrumentation. No need to call pprof.
$(OUTPUT)/$(PROJECT).$(EXPERIMENT).raw: raw/$(PROJECT).opt \
  raw/$(PROJECT).profile.out raw/$(PROJECT).calls raw/$(PROJECT).time
	$(VERB)echo "---------------------------------------------------------------" >> $@
	$(VERB)echo ">>> ========= '$(PROJECT).opt' Program" >> $@
	$(VERB)echo "---------------------------------------------------------------" >> $@
	$(VERB)awk -F "," '{user+=$$1; sys+=$$2; wall+=$$3} END{print "User time - " user; print "System time - " sys; print "Wall clock - " wall}' raw/$(PROJECT).time >> $@

$(OUTPUT)/$(PROJECT).$(EXPERIMENT).%: %/$(PROJECT).inst \
  %/$(PROJECT).profile.out %/$(PROJECT).calls %/$(PROJECT).time
	$(VERB)echo "---------------------------------------------------------------" >> $@
	$(VERB)echo ">>> ========= '$(PROJECT).opt' Program" >> $@
	$(VERB)echo "---------------------------------------------------------------" >> $@
	$(VERB)cat $*/$(PROJECT).polli >> $@
	$(VERB)$(PPROF) $*/$(PROJECT).profile.out 2>&1 | tee -a $@
	$(VERB)awk '{s+=$$1} END{print "Called libPAPI - " s}' $*/$(PROJECT).calls >> $@
	$(VERB)awk '{s+=$$1} END{ time = (s*$(PAPI_CALIBRATION)/$(TIME_UNIT)); \
	  print "Time spent in libPAPI (s) - " time}' $*/$(PROJECT).calls >> $@
	$(VERB)awk -F "," '{user+=$$1; sys+=$$2; wall+=$$3} END{print "User time - " user; print "System time - " sys; print "Wall clock - " wall}' $*/$(PROJECT).time >> $@
