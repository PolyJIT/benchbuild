LEVEL=../..
PROJECT=povray
DOMAIN=multimedia

TESTDIR=$(TESTINPUT)/$(DOMAIN)/$(PROJECT)

include $(LEVEL)/Makefile.common

#SCENE_DIR=scenes/
$(PROFBIN_F): $(RUN_F)
	-env POVRAY=$< \
	  INSTALL_DIR=$*/$(PROJECT_OUTDIR)/ \
	  OUTPUT_DIR=/tmp \
	  POVINI=$(TESTDIR)/cfg/.povray/3.6/povray.ini \
	  $(TESTDIR)/test/scripts/allscene.sh -d $(TESTDIR)/test
