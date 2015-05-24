PROJECT=xeigtsts
COMPILER = gfortran
LAPACK=..
DOMAIN=scientific
LEVEL=../../..

include $(LAPACK)/Makefile.lapack

$(PROFBIN_F): $(RUN_F)
	@echo NEP: Testing Nonsymmetric Eigenvalue Problem routines
	$^ < $(TESTDIR)/nep.in 2>&1
	@echo SEP: Testing Symmetric Eigenvalue Problem routines
	$^ < $(TESTDIR)/sep.in 2>&1
	@echo SVD: Testing Singular Value Decomposition routines
	$^ < $(TESTDIR)/svd.in 2>&1
	@echo SEC: Testing REAL Eigen Condition Routines
	$^ < $(TESTDIR)/sec.in 2>&1
	@echo SEV: Testing REAL Nonsymmetric Eigenvalue Driver
	$^ < $(TESTDIR)/sed.in 2>&1
	@echo SGG: Testing REAL Nonsymmetric Generalized Eigenvalue Problem routines
	$^ < $(TESTDIR)/sgg.in 2>&1
	@echo SGD: Testing REAL Nonsymmetric Generalized Eigenvalue Problem driver routines
	$^ < $(TESTDIR)/sgd.in 2>&1
	@echo SSB: Testing REAL Symmetric Eigenvalue Problem routines
	$^ < $(TESTDIR)/ssb.in 2>&1
	@echo SSG: Testing REAL Symmetric Generalized Eigenvalue Problem routines
	$^ < $(TESTDIR)/ssg.in 2>&1
	@echo SGEBAL: Testing the balancing of a REAL general matrix
	$^ < $(TESTDIR)/sbal.in 2>&1
	@echo SGEBAK: Testing the back transformation of a REAL balanced matrix
	$^ < $(TESTDIR)/sbak.in 2>&1
	@echo SGGBAL: Testing the balancing of a pair of REAL general matrices
	$^ < $(TESTDIR)/sgbal.in 2>&1
	@echo SGGBAK: Testing the back transformation of a pair of REAL balanced matrices
	$^ < $(TESTDIR)/sgbak.in 2>&1
	@echo SBB:  Testing banded Singular Value Decomposition routines
	$^ < $(TESTDIR)/sbb.in 2>&1
	@echo GLM: Testing Generalized Linear Regression Model routines
	$^ < $(TESTDIR)/glm.in 2>&1
	@echo GQR: Testing Generalized QR and RQ factorization routines
	$^ < $(TESTDIR)/gqr.in 2>&1
	@echo GSV: Testing Generalized Singular Value Decomposition routines
	$^ < $(TESTDIR)/gsv.in 2>&1
	@echo CSD: Testing CS Decomposition routines
	$^ < $(TESTDIR)/csd.in 2>&1
	@echo LSE: Testing Constrained Linear Least Squares routines
	$^ < $(TESTDIR)/lse.in 2>&1

