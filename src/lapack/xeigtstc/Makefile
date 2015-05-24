PROJECT=xeigtstc
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
	@echo CEC: Testing COMPLEX Eigen Condition Routines
	$^ < $(TESTDIR)/cec.in 2>&1
	@echo CES: Testing COMPLEX Nonsymmetric Schur Form Driver
	$^ < $(TESTDIR)/ced.in 2>&1
	@echo CGG: Testing COMPLEX Nonsymmetric Generalized Eigenvalue Problem routines
	$^ < $(TESTDIR)/cgg.in 2>&1
	@echo CGD: Testing COMPLEX Nonsymmetric Generalized Eigenvalue Problem driver routines
	$^ < $(TESTDIR)/cgd.in 2>&1
	@echo CHB: Testing Hermitian Eigenvalue Problem routines
	$^ < $(TESTDIR)/csb.in 2>&1
	@echo CSG: Testing Symmetric Generalized Eigenvalue Problem routines
	$^ < $(TESTDIR)/csg.in 2>&1
	@echo CGEBAL: Testing the balancing of a COMPLEX general matrix
	$^ < $(TESTDIR)/cbal.in 2>&1
	@echo CGEBAK: Testing the back transformation of a COMPLEX balanced matrix
	$^ < $(TESTDIR)/cbak.in 2>&1
	@echo CGGBAL: Testing the balancing of a pair of COMPLEX general matrices
	$^ < $(TESTDIR)/cgbal.in 2>&1
	@echo CGGBAK: Testing the back transformation of a pair of COMPLEX balanced matrices
	$^ < $(TESTDIR)/cgbak.in 2>&1
	@echo CBB:  Testing banded Singular Value Decomposition routines
	$^ < $(TESTDIR)/cbb.in 2>&1
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

