LEVEL=../..
PROJECT=avconv
DOMAIN=multimedia
TESTDIR=$(TESTINPUT)/multimedia/libav

include $(LEVEL)/Makefile.common

data= $(wildcard tests/*)
prj_data=$(addprefix $(abspath $(PROJECT_OUTDIR))/,$(data))

$(prj_data): prj_dir=$(abspath $(subst %,$*,$(PROJECT_OUTDIR)))
$(prj_data): $(data) | $(PROJECT_OUTDIR)/tests/.mkdir
	$(V_CP)cp -a $^ $(prj_dir)/tests/

$(PROJECT_OUTDIR)/Makefile: Makefile.libav
	$(V_CP)cp -a $^ $@

clean-%-$(PROJECT): products=$(abspath $(subst %,$*,$(prj_data)))
clean-%-$(PROJECT): product_mkfile=$(abspath $(subst %,$*,$(PROJECT_OUTDIR)/Makefile))
clean-%-$(PROJECT): prj_dir=$(abspath $(subst %,$*,$(PROJECT_OUTDIR)))
clean-%-$(PROJECT):
	$(V_RM)rm -f $(products)
	$(V_RM)rm -f $(product_mkfile)
	$(V_RM)-rmdir $(prj_dir)/tests

include Makefile.libav

.PHONY:
$(PROJECT_OUTDIR)/tests/.mkdir:
	$(V_MKD)mkdir -p $(subst /.mkdir,,$@)

$(PROFBIN_F): avconv_binary=$(abspath $(subst %,$*,$(RUN_F)))
$(PROFBIN_F): $(RUN_F) | $(prj_data) $(PROJECT_OUTDIR)/Makefile
	$(V_RUN)make TESTDIR=$(abspath $(TESTDIR)) $(MFLAGS) -i -C$(dir $(avconv_binary)) fate
	$(V_RUN)test -f $@ && touch $@
