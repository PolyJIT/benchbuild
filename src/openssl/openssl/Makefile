LEVEL=../../..
PROJECT=openssl
TESTDIR=$(TESTINPUT)/encryption/$(PROJECT)
DOMAIN=encryption

include $(LEVEL)/Makefile.common

%/$(PROFBIN_F): %/$(RUN_F)
	$(VERB)for f in `find $(TESTDIR)/certs -iname "*.pem"`; do \
	  OPENSSL_CONF=$(TESTDIR)/openssl.cnf \
	  ./$^ verify -CApath $(TESTDIR)/certs $$f ; \
	done;
