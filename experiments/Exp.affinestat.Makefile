$(OUTPUT)/$(PROJECT).$(EXPERIMENT).std: $(PROJECT).preopt
	$(VERB)echo "---------------------------------------------------------------" >> $@
	$(VERB)echo ">>> ========= '"$^"' Program" >> $@
	$(VERB)echo "---------------------------------------------------------------" >> $@
	$(VERB)opt -load $(POLLY) $(OPT_FLAGS) $(OPT_FLAGS_$*) $(VARIANT_$*) \
	  -polly-detect -polly-stat -stats -disable-output $^ 2>&1 | tee -a $@

$(OUTPUT)/$(PROJECT).$(EXPERIMENT).%: $(PROJECT).preopt
	$(VERB)touch $@
	$(VERB)echo "$(EXPERIMENT) is only available in 'std'"
