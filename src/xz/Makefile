LEVEL=../..
PROJECT=xz
DOMAIN=compression
TESTDIR=$(TESTINPUT)/compression/$(PROJECT)

include $(LEVEL)/Makefile.common

test_files_raw=text.html chicken.jpg control input.source liberty.jpg

test_files=$(addprefix $(TESTDIR)/,${test_files_raw})
test_files_to_build=$(addprefix $(PROJECT_OUTDIR)/,${test_files_raw})

clean-%-$(PROJECT): xz_products=$(subst %,$*,$(test_files_to_build))
clean-%-$(PROJECT):
	$(V_RM)rm -f $(xz_products)
	$(V_RM)rm -f $(addsuffix .bz2,$(xz_products))

$(test_files_to_build): prj_dir=$(subst %,$*,$(PROJECT_OUTDIR))
$(test_files_to_build): $(test_files)
	$(V_CP)cp $(test_files) $(prj_dir)

$(PROFBIN_F): xz_binary=$(abspath $(subst %,$*,$(RUN_F)))
$(PROFBIN_F): xz_prj_dir=$(abspath $(subst %,$*,$(PROJECT_OUTDIR)))
$(PROFBIN_F): $(RUN_F) $(test_files_to_build)
	 $(V_RUN)$< -k -f --compress -e -9 ${xz_prj_dir}/chicken.jpg
	 $(V_RUN)$< -k -f --compress -e -9 ${xz_prj_dir}/control
	 $(V_RUN)$< -k -f --compress -e -9 ${xz_prj_dir}/input.source
	 $(V_RUN)$< -k -f --compress -e -9 ${xz_prj_dir}/liberty.jpg
	 $(V_RUN)$< -k -f --compress -e -9 ${xz_prj_dir}/text.html
	 $(V_RUN)$< -k -f --decompress ${xz_prj_dir}/chicken.jpg.xz
	 $(V_RUN)$< -k -f --decompress ${xz_prj_dir}/control.xz
	 $(V_RUN)$< -k -f --decompress ${xz_prj_dir}/input.source.xz
	 $(V_RUN)$< -k -f --decompress ${xz_prj_dir}/liberty.jpg.xz
	 $(V_RUN)$< -k -f --decompress ${xz_prj_dir}/text.html.xz
