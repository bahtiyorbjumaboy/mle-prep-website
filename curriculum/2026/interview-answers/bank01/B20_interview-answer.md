---
type: interview-answer
item: "2026:bank01:B20"
title: "Three Views of Matrix-Vector Multiplication"
created: "2026-09-21"
updated: "2026-09-21"
tags:
  - linear-algebra
  - matrix-multiplication
  - multicollinearity
---

## Canonical Interview Question

Give me three different readings of the matrix product Ax, and explain the dummy-variable trap in terms of one of them.

## Mastery Answer

For $A\in\mathbb R^{m\times n}$ and $x\in\mathbb R^n$, there are three useful readings of $Ax$.

**Row view:** the $i$th output is the dot product of the $i$th row with $x$:
$$
(Ax)_i=a_i^Tx.
$$

**Column view:**
$$
Ax=x_1a_1+\cdots+x_na_n,
$$
so $Ax$ is a linear combination of the columns of $A$ and lies in $\operatorname{col}(A)$.

**Transformation view:** $A$ is a linear map from $\mathbb R^n$ to $\mathbb R^m$.

The dummy-variable trap is easiest to see with the column view. If a categorical variable with $k$ categories is encoded with all $k$ one-hot columns and the model also contains an intercept column of ones, then the dummy columns sum exactly to the intercept. The columns are linearly dependent, so the design matrix is rank deficient and $X^TX$ is singular. Dropping one dummy column or dropping the intercept removes the exact dependence; fitted values can remain equivalent while coefficient interpretation changes.

## Learn the Concepts

### Row view

If the rows of $A$ are $r_1^T,\ldots,r_m^T$,
$$
Ax=
\begin{bmatrix}
r_1^Tx\\
\vdots\\
r_m^Tx
\end{bmatrix}.
$$

This is the natural view for prediction: each row/example is scored by a dot product with a parameter vector.

### Column view

If
$$
A=[a_1\ \cdots\ a_n],
$$
then
$$
Ax=\sum_j x_ja_j.
$$

This view directly connects matrix multiplication to span and linear systems. $Ax=b$ is solvable exactly iff
$$
b\in\operatorname{col}(A).
$$

### Transformation view

A matrix is a linear operator:
$$
A:\mathbb R^n\to\mathbb R^m.
$$

This view is useful for composition, rank, null spaces, projections, neural-network linear layers, and embeddings.

### Dummy-variable trap

Suppose a categorical feature has three levels with dummy columns $d_1,d_2,d_3$. Every row belongs to exactly one category, so
$$
d_1+d_2+d_3=\mathbf 1.
$$

If the intercept column $\mathbf 1$ is also present,
$$
\mathbf 1-d_1-d_2-d_3=0,
$$
which is an exact nontrivial linear dependence.

That makes the coefficient vector non-unique: multiple coefficient assignments produce the same fitted values.

### Exact versus near multicollinearity

The dummy-variable trap is **exact** multicollinearity. Near multicollinearity means the columns are almost dependent. The matrix can remain full rank but have a very small singular value, making the problem ill-conditioned.

“Correlated features” is only an informal proxy. The precise issue is near-linear dependence among columns.

## Required / Important Follow-ups

### Does standardizing fix the dummy-variable trap?

No. Standardization changes scales but does not remove an exact linear dependence.

### Why can dropping one dummy or dropping the intercept give the same fitted values?

Both parameterizations can span the same prediction space. What changes is the coordinate system used to describe those predictions, so coefficient interpretation changes.

### What is the numerical signature of near multicollinearity?

A small singular value and a large condition number. Numerical rank can become tolerance-dependent even though algebraic rank is still full.
