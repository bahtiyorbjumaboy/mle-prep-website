---
type: interview-answer
item: "2026:bank01:B19"
title: "Span, Linear Independence, Basis, and Rank"
created: "2026-09-21"
updated: "2026-09-21"
tags:
  - linear-algebra
  - rank
  - basis
---

## Canonical Interview Question

Define span, linear independence, basis, and rank, and state how they relate. Why is row rank equal to column rank, and what is the rank of a product AB bounded by?

## Mastery Answer

The **span** of vectors is the set of all linear combinations of those vectors. A set is **linearly independent** if the only coefficients that produce the zero vector are all zero; equivalently, no vector can be written as a linear combination of the others. A **basis** is a linearly independent spanning set, and the **dimension** of a subspace is the number of vectors in any basis.

For a matrix $A$, the **rank** is the dimension of its column space, equivalently the dimension of its row space. Row rank equals column rank because row reduction reveals the same number of pivots from both perspectives: the nonzero rows of echelon form form a basis for the row space, while the corresponding pivot columns of the **original** matrix form a basis for the column space.

For compatible matrices,
$$
\operatorname{rank}(AB)\le \min(\operatorname{rank}(A),\operatorname{rank}(B)).
$$
Every column of $AB$ lies in $\operatorname{col}(A)$, so the product cannot have rank greater than $A$. Also $\operatorname{null}(B)\subseteq \operatorname{null}(AB)$, so the product cannot retain more independent input directions than $B$.

## Learn the Concepts

### Span

For vectors $v_1,\ldots,v_k$,
$$
\operatorname{span}\{v_1,\ldots,v_k\}
=
\left\{\sum_i c_i v_i\right\}.
$$

Span answers a reachability question: what vectors can be constructed from the available directions?

For
$$
A=[a_1\ \cdots\ a_n],
$$
we have
$$
Ax=x_1a_1+\cdots+x_na_n,
$$
so all possible outputs of $A$ are exactly its column space.

### Linear independence

$v_1,\ldots,v_k$ are linearly independent if
$$
\sum_i c_i v_i=0
$$
implies every $c_i=0$.

For the columns of $A$, linear dependence is equivalent to the existence of a nonzero solution of
$$
Ax=0.
$$

### Basis and dimension

A basis spans a subspace without redundancy. Every vector in the subspace has a unique coordinate representation in that basis. The number of basis vectors is the dimension.

### Rank

For $A\in\mathbb R^{m\times n}$,
$$
\operatorname{rank}(A)
=
\dim(\operatorname{col}(A))
=
\dim(\operatorname{row}(A)).
$$

Rank is the number of independent directions that survive the transformation.

### Why row rank equals column rank

Gaussian elimination produces an echelon form with $r$ pivots.

- The $r$ nonzero rows of echelon form form a basis for the row space.
- The $r$ pivot **indices** identify $r$ columns of the original matrix that form a basis for the original column space.

Therefore both dimensions equal $r$.

A useful precision point: row operations preserve the row space and preserve dependence relationships among columns, but they do not preserve the literal column space.

### Rank of a product

If $A\in\mathbb R^{m\times k}$ and $B\in\mathbb R^{k\times n}$, then
$$
\operatorname{col}(AB)\subseteq \operatorname{col}(A),
$$
so
$$
\operatorname{rank}(AB)\le \operatorname{rank}(A).
$$

Also,
$$
Bx=0\implies ABx=0,
$$
so
$$
\operatorname{null}(B)\subseteq \operatorname{null}(AB).
$$

By rank-nullity, this gives
$$
\operatorname{rank}(AB)\le \operatorname{rank}(B).
$$

## Required / Important Follow-ups

### Why must pivot columns be taken from the original matrix?

Row operations change the actual column vectors. The reduced matrix tells us which **column indices** are pivots, but the basis for the original column space must use those columns from the original matrix.

### What does rank deficiency mean in an ML design matrix?

At least one feature column is an exact linear combination of others. Ordinary least squares then has non-identifiable coefficients unless an additional constraint, pseudoinverse convention, or regularization is introduced.

### Can $\operatorname{rank}(AB)$ be strictly less than both ranks?

Yes. The image of $B$ may enter directions that $A$ sends to zero.
