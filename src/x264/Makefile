LEVEL=../..
PROJECT = x264
DOMAIN=multimedia

TESTDIR = $(TESTINPUT)/$(DOMAIN)/$(PROJECT)
include $(LEVEL)/Makefile.common

# --- From: x264 top-level Makefile
# These should cover most of the important codepaths
OPT0 = --frames 5 --crf 30 -b1 -m1 -r1 --me dia --no-cabac --direct temporal --ssim --no-weightb
OPT1 = --frames 5 --crf 16 -b2 -m3 -r3 --me hex --no-8x8dct --direct spatial --no-dct-decimate -t0  --slice-max-mbs 50
OPT2 = --frames 5 --crf 26 -b4 -m5 -r2 --me hex --cqm jvt --nr 100 --psnr --no-mixed-refs --b-adapt 2 --slice-max-size 1500
OPT3 = --frames 5 --crf 18 -b3 -m9 -r5 --me umh -t1 -A all --b-pyramid normal --direct auto --no-fast-pskip --no-mbtree
OPT4 = --frames 5 --crf 22 -b3 -m7 -r4 --me esa -t2 -A all --psy-rd 1.0:1.0 --slices 4
OPT5 = --frames 5 --crf 24 -b3 -m10 -r3 --me tesa -t2
OPT6 = --frames 5 -q0 -m9 -r2 --me hex -Aall
OPT7 = --frames 5 -q0 -m2 -r1 --me hex --no-cabac
VIDS = $(TESTDIR)/tbbt-small.y4m

$(PROFBIN_F): $(RUN_F)
	$(foreach V, $(VIDS), $(VERB)$< $(OPT7) $(V) --threads 1 -o /dev/null ;)
	$(foreach V, $(VIDS), $(VERB)$< $(OPT6) $(V) --threads 1 -o /dev/null ;)
	$(foreach V, $(VIDS), $(VERB)$< $(OPT5) $(V) --threads 1 -o /dev/null ;)
	$(foreach V, $(VIDS), $(VERB)$< $(OPT4) $(V) --threads 1 -o /dev/null ;)
	$(foreach V, $(VIDS), $(VERB)$< $(OPT3) $(V) --threads 1 -o /dev/null ;)
	$(foreach V, $(VIDS), $(VERB)$< $(OPT2) $(V) --threads 1 -o /dev/null ;)
	$(foreach V, $(VIDS), $(VERB)$< $(OPT1) $(V) --threads 1 -o /dev/null ;)
