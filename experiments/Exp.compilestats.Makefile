$(OUTPUT)/$(PROJECT).$(EXPERIMENT).caddy: $(PROJECT).preopt
	$(VERB)echo "---------------------------------------------------------------" >> $@
	$(VERB)echo ">>> ========= '"$^"' Program" >> $@
	$(VERB)echo "---------------------------------------------------------------" >> $@
	(cd caddy &&  $(VERB)opt -load $(POLLY) -stats -basicaa -tbaa $(VARIANT_std) -polly-export-jscop -S -disable-output ../$^) 2>&1 | tee -a $@
	(cd caddy && $(VERB)opt -load $(POLLY) -stats -basicaa -tbaa $(VARIANT_caddy) -polly-allow-nonaffine -caddy-export-cscop-pass -S -disable-output ../$^) 2>&1 | tee -a $@

$(OUTPUT)/$(PROJECT).$(EXPERIMENT).%: $(PROJECT).preopt
	$(VERB)echo "---------------------------------------------------------------" >> $@
	$(VERB)echo ">>> ========= '$(PROJECT).opt' Program" >> $@
	$(VERB)echo "---------------------------------------------------------------" >> $@
	$(VERB)opt -strip-debug -load $(POLLY) $(OPT_FLAGS) $(OPT_FLAGS_$*) $(VARIANT_$*) \
	  -polly-detect -stats -disable-output $^ 2>&1 | tee -a $@
