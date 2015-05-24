LEVEL=../../..
PROJECT=ecdsa
DOMAIN=encryption

include $(LEVEL)/Makefile.common

%/$(PROFBIN_F): %/$(RUN_F)
	./$^
	mv papi.profile.out $@
