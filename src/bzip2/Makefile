LEVEL=../..
PROJECT=bzip2
DOMAIN=compression
TESTDIR=$(TESTINPUT)/compression/$(PROJECT)

include $(LEVEL)/Makefile.common

BZIP2_COMPRESS = -f -z -k
BZIP2_DECOMPRESS = -f -k

test_files_raw=text.html chicken.jpg control input.source liberty.jpg

test_files=$(addprefix $(TESTDIR)/,${test_files_raw})
test_files_to_build=$(addprefix $(PROJECT_OUTDIR)/,${test_files_raw})

clean-%-$(PROJECT): bzip_products=$(subst %,$*,$(test_files_to_build))
clean-%-$(PROJECT):
	$(V_RM)rm -f $(bzip_products)
	$(V_RM)rm -f $(addsuffix .bz2,$(bzip_products))

$(test_files_to_build): prj_dir=$(subst %,$*,$(PROJECT_OUTDIR))
$(test_files_to_build): $(test_files)
	$(V_CP)cp $(test_files) $(prj_dir)

$(PROFBIN_F): bzip2_binary=$(abspath $(subst %,$*,$(RUN_F)))
$(PROFBIN_F): bzip2_prj_dir=$(abspath $(subst %,$*,$(PROJECT_OUTDIR)))
$(PROFBIN_F): $(RUN_F) $(test_files_to_build)
	$(V_RUN)$< $(BZIP2_COMPRESS) --best $(bzip2_prj_dir)/text.html
	#$(V_RUN)$< $(BZIP2_DECOMPRESS) --decompress $(bzip2_prj_dir)/text.html.bz2
	#$(V_RUN)$< $(BZIP2_COMPRESS) --best $(bzip2_prj_dir)/chicken.jpg
	#$(V_RUN)$< $(BZIP2_DECOMPRESS) --decompress $(bzip2_prj_dir)/chicken.jpg.bz2
	#$(V_RUN)$< $(BZIP2_COMPRESS) --best $(bzip2_prj_dir)/control
	#$(V_RUN)$< $(BZIP2_DECOMPRESS) --decompress $(bzip2_prj_dir)/control.bz2
	#$(V_RUN)$< $(BZIP2_COMPRESS) --best $(bzip2_prj_dir)/input.source
	#$(V_RUN)$< $(BZIP2_DECOMPRESS) --decompress $(bzip2_prj_dir)/input.source.bz2
	#$(V_RUN)$< $(BZIP2_COMPRESS) --best $(bzip2_prj_dir)/liberty.jpg
	#$(V_RUN)$< $(BZIP2_DECOMPRESS) --decompress $(bzip2_prj_dir)/liberty.jpg.bz2
