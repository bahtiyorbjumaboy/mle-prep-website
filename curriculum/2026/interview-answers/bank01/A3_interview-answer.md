---
type: interview-answer
item: "2026:bank01:A3"
title: "Least Squares Geometry, Solvers, and the Pseudoinverse"
created: "2026-09-21"
updated: "2026-09-21"
tags:
  - linear-algebra
  - least-squares
  - pseudoinverse
  - qr
  - svd
---

## Canonical Interview Question

Explain least squares geometrically and algebraically: projection, normal equations, residual orthogonality, full-rank versus rank-deficient cases, no/one/many solutions of Ax=b, and what the pseudoinverse returns.

## Mastery Answer

For an overdetermined system $Xw\approx y$, exact equality may be impossible because $y$ may lie outside $\operatorname{col}(X)$. Least squares chooses the reachable vector $X\hat w$ closest to $y$, so $X\hat w$ is the orthogonal projection of $y$ onto $\operatorname{col}(X)$.

The residual is
$$
r=y-X\hat w.
$$
At the optimum it is orthogonal to every column of $X$:
$$
X^Tr=0.
$$
Therefore
$$
X^T(y-X\hat w)=0,
$$
giving the normal equations
$$
X^TX\hat w=X^Ty.
$$

For a general system $Ax=b$:

- if $b\notin\operatorname{col}(A)$, there is no exact solution;
- if $b\in\operatorname{col}(A)$ and $\operatorname{null}(A)=\{0\}$, there is exactly one solution;
- if $b\in\operatorname{col}(A)$ and the null space is nontrivial, there are infinitely many solutions:
$$
x=x_p+z,\qquad z\in\operatorname{null}(A).
$$

Thus uniqueness for a rectangular matrix requires **full column rank**, not merely an ambiguous statement that the matrix is “full rank.”

If
$$
A=U\Sigma V^T,
$$
the Moore-Penrose pseudoinverse is
$$
A^+=V\Sigma^+U^T,
$$
where nonzero singular values are reciprocated. $A^+b$ gives the least-squares minimizer; if multiple minimizers exist, it selects the minimum-Euclidean-norm one. If exact solutions exist but are nonunique, it returns the minimum-norm exact solution.

## Learn the Concepts

### Geometry of least squares

The column space contains every vector the model can produce. If $y$ is outside that subspace, the best approximation is its orthogonal projection onto the subspace.

The residual from a closest-point projection must be perpendicular to the subspace. Since the columns of $X$ span the subspace,
$$
x_j^Tr=0
$$
for every column $x_j$, compactly
$$
X^Tr=0.
$$

### Normal equations

Substitute
$$
r=y-X\hat w:
$$
$$
X^T(y-X\hat w)=0.
$$

Rearranging:
$$
X^TX\hat w=X^Ty.
$$

If $X$ has full column rank, $X^TX$ is invertible and the coefficient solution is unique.

### Rank-deficient least squares

If $X$ is rank deficient, multiple coefficient vectors can generate the same fitted vector. The prediction $X\hat w$ can still be uniquely defined even when $\hat w$ is not.

### Pseudoinverse

The SVD exposes independent input/output directions:
$$
A=U\Sigma V^T.
$$

The pseudoinverse reverses every nonzero singular direction:
$$
A^+=V\Sigma^+U^T.
$$

Zero singular directions cannot be inverted, so they receive zero in $\Sigma^+$.

This produces the least-squares solution while discarding unsupported null-space components, which is why the resulting coefficient vector has minimum norm.

### Solver choices

The normal equations are cheap and simple but square the condition number.

QR avoids forming $X^TX$ and is a strong stable default for full-rank least squares.

SVD is more expensive but directly exposes singular values, numerical rank, and null-space structure, making it the most robust choice for severe ill-conditioning or rank deficiency.

## Required / Important Follow-ups

### Compare the normal equations, QR factorization, and SVD as ways to solve least squares. Which would you choose for a well-conditioned full-rank matrix, an ill-conditioned matrix, and a rank-deficient matrix, and why?

**Well-conditioned full-column-rank:** normal equations can be acceptable when simplicity and low cost matter, although QR is a safer default.

**Ill-conditioned but full-rank:** prefer QR because it avoids squaring the condition number. If conditioning is severe or explicit singular-value diagnostics are needed, prefer SVD.

**Rank-deficient:** prefer SVD because it exposes zero or tiny singular values and directly yields the minimum-norm least-squares solution. Pivoted QR can estimate numerical rank, but ordinary QR does not expose singular values or provide the same clean minimum-norm construction.

A useful hierarchy is:

- normal equations: cheapest, least stable;
- QR: standard stable default;
- SVD: most robust and informative, but typically most expensive.

### Does pivoted QR expose singular values?

No. It can reveal or estimate numerical rank through column pivoting and diagonal structure in $R$, but singular values are specifically exposed by the SVD.

### When does $(A^TA)^{-1}A^T$ equal the pseudoinverse?

When $A$ has full column rank. It is not the general definition.
