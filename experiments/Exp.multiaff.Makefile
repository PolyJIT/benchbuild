$(OUTPUT)/$(PROJECT).$(EXPERIMENT).caddy: $(PROJECT).preopt
	$(VERB)echo "---------------------------------------------------------------" >> $@
	$(VERB)echo ">>> ========= '"$^"' Program" >> $@
	$(VERB)echo "---------------------------------------------------------------" >> $@
	$(VERB)opt -stats -load $(POLLY) $(OPT_FLAGS) $(OPT_FLAGS_caddy) -disable-output $^ 2>&1 | tee -a $@

$(OUTPUT)/$(PROJECT).$(EXPERIMENT).%: $(PROJECT).preopt
	$(VERB)touch $@
	$(VERB)echo "$(EXPERIMENT) is only available in 'caddy'"
