$(OUTPUT)/$(PROJECT).$(EXPERIMENT).%: $(OUTPUT)/$(PROJECT).pprof.%
	$(VERB)echo "Domain - $(DOMAIN)" >> $(@:-append.std=.std)
	$(VERB)echo "Domain - $(DOMAIN)" >> $(@:-append.std=.jit)
	$(VERB)echo "Domain - $(DOMAIN)" >> $(@:-append.std=.caddy)
	$(VERB)echo "Lines of Code - $(wc -l $$(PROJECT).bc)" >> $(@:-append.std=.std)
	$(VERB)echo "Lines of Code - $(wc -l $$(PROJECT).bc)" >> $(@:-append.std=.jit)
	$(VERB)echo "Lines of Code - $(wc -l $$(PROJECT).bc)" >> $(@:-append.std=.caddy)
