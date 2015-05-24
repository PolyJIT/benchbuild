$(OUTPUT)/$(PROJECT).$(EXPERIMENT).std: $(PROJECT).preopt
	$(VERB)echo "---------------------------------------------------------------" >> $@
	$(VERB)echo ">>> ========= '"$^"' Program" >> $@
	$(VERB)echo "---------------------------------------------------------------" >> $@
	$(VERB)opt -stats -load $(POLLY)  -polly-scops -polly-ignore-aliasing $(OPT_FLAGS) $(OPT_FLAGS_std) -disable-output \
	  $^ 2>&1 | tee -a $@

$(OUTPUT)/$(PROJECT).$(EXPERIMENT).%: $(PROJECT).preopt
	$(VERB)touch $@
	$(VERB)echo "$(EXPERIMENT) is only available in 'std'"
