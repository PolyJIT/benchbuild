PROJECT=xeigtstd
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
	@echo DEC: Testing DOUBLE PRECISION Eigen Condition Routines
	$^ < $(TESTDIR)/dec.in 2>&1
	@echo DEV: Testing DOUBLE PRECISION Nonsymmetric Eigenvalue Driver
	$^ < $(TESTDIR)/ded.in 2>&1
	@echo DGG: Testing DOUBLE PRECISION Nonsymmetric Generalized Eigenvalue Problem routines
	$^ < $(TESTDIR)/dgg.in 2>&1
	@echo DGD: Testing DOUBLE PRECISION Nonsymmetric Generalized Eigenvalue Problem driver routines
	$^ < $(TESTDIR)/dgd.in 2>&1
	@echo DSB: Testing DOUBLE PRECISION Symmetric Eigenvalue Problem routines
	$^ < $(TESTDIR)/dsb.in 2>&1
	@echo DSG: Testing DOUBLE PRECISION Symmetric Generalized Eigenvalue Problem routines
	$^ < $(TESTDIR)/dsg.in 2>&1
	@echo DGEBAL: Testing the balancing of a DOUBLE PRECISION general matrix
	$^ < $(TESTDIR)/dbal.in 2>&1
	@echo DGEBAK:  Testing the back transformation of a DOUBLE PRECISION balanced matrix
	$^ < $(TESTDIR)/dbak.in 2>&1
	@echo DGGBAL: Testing the balancing of a pair of DOUBLE PRECISION general matrices
	$^ < $(TESTDIR)/dgbal.in 2>&1
	@echo DGGBAK: Testing the back transformation of a pair of DOUBLE PRECISION balanced matrices
	$^ < $(TESTDIR)/dgbak.in 2>&1
	@echo DBB:  Testing banded Singular Value Decomposition routines
	$^ < $(TESTDIR)/dbb.in 2>&1
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

