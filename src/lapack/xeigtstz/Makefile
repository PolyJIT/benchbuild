PROJECT=xeigtstz
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
	@echo ZEC: Testing COMPLEX16 Eigen Condition Routines
	$^ < $(TESTDIR)/zec.in 2>&1
	@echo ZES: Testing COMPLEX16 Nonsymmetric Schur Form Driver
	$^ < $(TESTDIR)/zed.in 2>&1
	@echo ZGG: Testing COMPLEX16 Nonsymmetric Generalized Eigenvalue Problem routines
	$^ < $(TESTDIR)/zgg.in 2>&1
	@echo ZGD: Testing COMPLEX16 Nonsymmetric Generalized Eigenvalue Problem driver routines
	$^ < $(TESTDIR)/zgd.in 2>&1
	@echo ZHB: Testing Hermitian Eigenvalue Problem routines
	$^ < $(TESTDIR)/zsb.in 2>&1
	@echo ZSG: Testing Symmetric Generalized Eigenvalue Problem routines
	$^ < $(TESTDIR)/zsg.in 2>&1
	@echo ZGEBAL: Testing the balancing of a COMPLEX16 general matrix
	$^ < $(TESTDIR)/zbal.in 2>&1
	@echo ZGEBAK: Testing the back transformation of a COMPLEX16 balanced matrix
	$^ < $(TESTDIR)/zbak.in 2>&1
	@echo ZGGBAL: Testing the balancing of a pair of COMPLEX general matrices
	$^ < $(TESTDIR)/zgbal.in 2>&1
	@echo ZGGBAK: Testing the back transformation of a pair of COMPLEX16 balanced matrices
	$^ < $(TESTDIR)/zgbak.in 2>&1
	@echo ZBB: Testing banded Singular Value Decomposition routines
	$^ < $(TESTDIR)/zbb.in 2>&1
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
