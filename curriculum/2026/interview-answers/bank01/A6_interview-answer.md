---
type: interview-answer
item: "2026:bank01:A6"
title: "Eigendecomposition, SVD, and PCA"
created: "2026-09-21"
updated: "2026-09-21"
tags:
  - linear-algebra
  - svd
  - pca
  - eigendecomposition
---

## Canonical Interview Question

Compare eigendecomposition, SVD, and PCA as related spectral tools. State when each decomposition exists, the orthogonality guarantees, derive PCA from covariance and from the SVD of centered data, explain centering versus scaling, and identify a supervised-learning case where PCA can hurt.

## Mastery Answer

Eigendecomposition, SVD, and PCA are closely related, but they answer different questions.

For a square matrix $A \in \mathbb{R}^{d \times d}$, an eigendecomposition

$$
A = Q\Lambda Q^{-1}
$$

exists when $A$ is diagonalizable, meaning it has $d$ linearly independent eigenvectors. A real symmetric matrix is the important special case: by the spectral theorem, all eigenvalues are real and the eigenvectors can be chosen orthonormally, so

$$
A = Q\Lambda Q^T.
$$

SVD is more general. Every real matrix $X \in \mathbb{R}^{n \times d}$ has an SVD

$$
X = U\Sigma V^T.
$$

In the full SVD, $U$ and $V$ are square orthogonal matrices. In the reduced rank-$r$ SVD,

$$
U \in \mathbb{R}^{n \times r}, \qquad
\Sigma \in \mathbb{R}^{r \times r}, \qquad
V \in \mathbb{R}^{d \times r},
$$

and the columns of $U$ and $V$ are orthonormal. The columns of $U$ span $\operatorname{col}(X)$, while the columns of $V$ span $\operatorname{row}(X)=\operatorname{col}(X^T)$.

SVD connects directly to eigendecomposition because

$$
X^T X = V\Sigma^2 V^T
$$

and

$$
X X^T = U\Sigma^2 U^T.
$$

Therefore, the right singular vectors are eigenvectors of $X^T X$, the left singular vectors are eigenvectors of $X X^T$, and the nonzero eigenvalues are the squared singular values.

For PCA, let $X$ be centered data with $n$ observations and $d$ features. The sample covariance matrix is

$$
C = \frac{1}{n-1}X^T X.
$$

PCA takes the eigenvectors of $C$, sorted by descending eigenvalue. Each eigenvector gives a principal direction, and its eigenvalue is the variance captured in that direction.

Substituting the SVD gives

$$
C = \frac{1}{n-1}V\Sigma^2V^T.
$$

So the PCA directions are the columns of $V$, and the explained variance of component $i$ is

$$
\frac{\sigma_i^2}{n-1}.
$$

The projected PCA coordinates, or scores, are

$$
XV = U\Sigma.
$$

Thus PCA can be computed directly from the SVD of centered data without explicitly forming the covariance matrix.

Centering and scaling do different things. Centering is fundamental to ordinary PCA because PCA is meant to describe variation around the mean. Without centering, $X^TX$ is a second-moment matrix, so mean structure contaminates the directions and a leading component can mostly reflect the offset from the origin rather than variation around the data mean. Scaling is optional: standardizing features is appropriate when arbitrary units or magnitude differences should not determine which directions appear most important. If raw variance itself is meaningful, scaling may be undesirable.

PCA can hurt a supervised model because PCA is unsupervised: it preserves directions with high input variance, not directions with high predictive value for $y$. A low-variance feature combination can be highly predictive and still be discarded by dimensionality reduction. PCA can also reduce interpretability because each principal component is a mixture of the original features.

## Learn the Concepts

### 1. Eigendecomposition: invariant directions of a square operator

An eigenvector $q$ of $A$ satisfies

$$
Aq = \lambda q.
$$

The matrix changes only the vector's scale, not its direction. If a square matrix has enough linearly independent eigenvectors to form a basis, every vector can be expressed in those eigen-directions and the matrix can be diagonalized:

$$
A = Q\Lambda Q^{-1}.
$$

A generic square matrix need not be diagonalizable. Symmetric matrices are much better behaved: the spectral theorem guarantees an orthonormal eigenbasis, so $Q^{-1}=Q^T$. This orthogonality is why symmetric matrices such as covariance matrices are especially convenient in ML.

### 2. SVD: a decomposition that always exists

SVD applies even when a matrix is rectangular or rank-deficient:

$$
X = U\Sigma V^T.
$$

A useful geometric reading is:

1. $V^T$ expresses an input vector in orthogonal feature-space directions.
2. $\Sigma$ stretches each direction by its singular value.
3. $U$ maps those stretched coordinates into orthogonal output/sample-space directions.

For rank $r$, only $r$ singular values are nonzero. In the reduced SVD, this keeps only the subspaces that the matrix actually uses.

The subspace roles are worth being precise about. For any vector $a$,

$$
Xa = U\Sigma V^Ta,
$$

so every vector in $\operatorname{col}(X)$ lies in the span of the columns of $U$. Because both spaces have dimension $r$, they are equal. Applying the same logic to $X^T=V\Sigma U^T$ gives

$$
\operatorname{col}(X^T)=\operatorname{col}(V),
$$

so $V$ spans the row space of $X$, which lives in feature space.

### 3. Why SVD and eigendecomposition meet at $X^TX$

Starting from the SVD,

$$
X^TX
= (U\Sigma V^T)^T(U\Sigma V^T)
= V\Sigma U^TU\Sigma V^T
= V\Sigma^2V^T.
$$

Because $U^TU=I$, this is exactly an eigendecomposition of the symmetric PSD matrix $X^TX$. The same argument gives $XX^T=U\Sigma^2U^T$.

This identity is the bridge from SVD to PCA.

### 4. PCA from covariance

Assume the rows of $X$ are centered observations. The variance of the data after projection onto a unit vector $v$ is

$$
\operatorname{Var}(Xv)
= \frac{1}{n-1}v^T X^TXv.
$$

PCA asks for the unit direction maximizing this quantity. The Rayleigh quotient is maximized by the eigenvector of $X^TX$ with the largest eigenvalue. Subsequent components maximize remaining variance while being orthogonal to earlier components.

Therefore PCA is fundamentally an eigenproblem on the covariance matrix.

### 5. PCA directly from SVD

If

$$
X = U\Sigma V^T,
$$

then

$$
\frac{1}{n-1}X^TX
= V\frac{\Sigma^2}{n-1}V^T.
$$

This immediately identifies:

- principal directions: columns of $V$;
- component variances: $\sigma_i^2/(n-1)$;
- PCA scores: $XV=U\Sigma$.

For a rank-$r$ matrix,

$$
\operatorname{rank}(X^TX)=\operatorname{rank}(X)=r.
$$

So the covariance matrix has only $r$ positive eigenvalues. There are therefore exactly $r$ principal directions with nonzero variance; the remaining feature-space directions have zero variance on this centered dataset.

### 6. Centering versus scaling

Centering subtracts each feature mean. It changes the origin so PCA measures spread around the empirical mean rather than distance from the coordinate origin.

Scaling changes the relative weighting of features. If one feature is measured in centimeters and another in meters, the centimeter feature can dominate covariance simply because of units. Standardization to unit variance removes that unit effect, but it also changes the question: PCA on standardized data emphasizes correlation structure rather than raw covariance structure.

So:

- center almost always for ordinary PCA;
- scale only when the modeling meaning of feature units justifies it.

### 7. When PCA can hurt supervised learning

PCA never looks at the target. Suppose a dataset has one low-variance direction that almost perfectly separates two classes and several high-variance nuisance directions unrelated to the label. PCA can discard the low-variance predictive direction because it optimizes reconstruction variance, not predictive loss.

Other practical costs include:

- loss of feature-level interpretability;
- extra preprocessing and versioning at serving time;
- possible mismatch if the covariance structure drifts;
- unnecessary information loss when the downstream model already handles correlated or high-dimensional inputs well.

## Required / Important Follow-ups

### Reduced-SVD shapes and subspace roles

If $X \in \mathbb{R}^{n\times d}$ has rank $r<\min(n,d)$, the reduced SVD has

$$
U \in \mathbb{R}^{n\times r}, \qquad
\Sigma \in \mathbb{R}^{r\times r}, \qquad
V \in \mathbb{R}^{d\times r}.
$$

The columns of $U$ span the column space of $X$. The columns of $V$ span the row space of $X$, equivalently $\operatorname{col}(X^T)$, which is the feature-space subspace relevant to PCA.

### Why are there only $r$ nonzero principal components?

Because

$$
\operatorname{rank}(X^TX)=\operatorname{rank}(X)=r.
$$

A symmetric matrix of rank $r$ has exactly $r$ nonzero eigenvalues. Since the covariance matrix is just $X^TX/(n-1)$, it has $r$ positive eigenvalues and therefore $r$ principal directions with nonzero variance.
