LEVEL=../..
PROJECT=gzip
DOMAIN=compression
TESTDIR=$(TESTINPUT)/compression/$(PROJECT)

include $(LEVEL)/Makefile.common

test_files_raw=text.html chicken.jpg control input.source liberty.jpg
test_files=$(addprefix ${TESTDIR}/,${test_files_raw})
test_files_to_build=$(addprefix $(PROJECT_OUTDIR)/,${test_files_raw})

$(test_files_to_build): prj_dir=$(subst %,$*,$(PROJECT_OUTDIR))
$(test_files_to_build): $(test_files)
	$(V_CP)cp $(test_files) $(prj_dir)

clean-%-$(PROJECT): gzip_products=$(subst %,$*,$(test_files_to_build))
clean-%-$(PROJECT):
	$(V_RM)rm -f $(gzip_products)
	$(V_RM)rm -f $(addsuffix .gz,$(gzip_products))

$(PROFBIN_F): gzip_binary=$(subst %,$*,$(RUN_F))
$(PROFBIN_F): gzip_prj_dir=$(subst %,$*,$(PROJECT_OUTDIR))
$(PROFBIN_F): $(RUN_F) $(test_files_to_build)
	$(V_RUN)./$^ -k -f --best ${gzip_prj_dir}/text.html
	$(V_RUN)./$^ -k -f --best ${gzip_prj_dir}/chicken.jpg
	$(V_RUN)./$^ -k -f --best ${gzip_prj_dir}/control
	$(V_RUN)./$^ -k -f --best ${gzip_prj_dir}/input.source
	$(V_RUN)./$^ -k -f --best ${gzip_prj_dir}/liberty.jpg
	$(V_RUN)./$^ -k -f --decompress ${gzip_prj_dir}/text.html.gz
	$(V_RUN)./$^ -k -f --decompress ${gzip_prj_dir}/chicken.jpg.gz
	$(V_RUN)./$^ -k -f --decompress ${gzip_prj_dir}/control.gz
	$(V_RUN)./$^ -k -f --decompress ${gzip_prj_dir}/input.source.gz
	$(V_RUN)./$^ -k -f --decompress ${gzip_prj_dir}/liberty.jpg.gz
