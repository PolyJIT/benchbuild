LEVEL=../..
PROJECT=ccrypt
DOMAIN=encryption

TESTDIR=$(TESTINPUT)/encryption/$(PROJECT)
include $(LEVEL)/Makefile.common

clean-%-$(PROJECT): ccrypt_prj_dir=$(subst %,$*,$(PROJECT_OUTDIR))
clean-%-$(PROJECT):
	$(V_RM)rm -f $(ccrypt_prj_dir)/check

$(PROFBIN_F): ccrypt=$(abspath $(subst %,$*,$(RUN_F)))
$(PROFBIN_F): ccrypt_prj_dir=$(abspath $(subst %,$*,$(PROJECT_OUTDIR)))
$(PROFBIN_F): $(RUN_F)
	$(VERB)ln -s $(abspath $(TESTDIR)/check) $(ccrypt_prj_dir)
	CCRYPT="$(ccrypt) -f" \
	srcdir="$(ccrypt_prj_dir)/check" \
	       $(ccrypt_prj_dir)/check/ccrypt-check.sh
	srcdir="$(ccrypt_prj_dir)/check" \
	CCRYPT='$(ccrypt) -f' \
	       $(ccrypt_prj_dir)/check/length-check.sh
