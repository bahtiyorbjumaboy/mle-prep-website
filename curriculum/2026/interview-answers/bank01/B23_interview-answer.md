---
type: interview-answer
item: "2026:bank01:B23"
title: "Dot Products, Orthogonality, and Projection"
created: "2026-09-21"
updated: "2026-09-21"
tags:
  - linear-algebra
  - dot-product
  - projection
---

## Canonical Interview Question

Define the dot product geometrically and algebraically. Derive the projection of one vector onto another, and state what a zero dot product does and does not imply.

## Mastery Answer

Algebraically,
$$
u^Tv=\sum_i u_iv_i.
$$

Geometrically, for nonzero vectors,
$$
u^Tv=\|u\|\,\|v\|\cos\theta.
$$

So the sign indicates whether the angle is acute, right, or obtuse.

To project $u$ onto a nonzero vector $v$, write the projection as $cv$ and require the residual $u-cv$ to be orthogonal to $v$:
$$
v^T(u-cv)=0.
$$
Therefore
$$
c=\frac{v^Tu}{v^Tv},
$$
and
$$
\operatorname{proj}_v(u)=\frac{v^Tu}{v^Tv}v.
$$

A zero dot product between nonzero vectors means they are orthogonal. For centered data vectors, zero dot product corresponds to zero sample covariance up to the scaling convention. But zero covariance does **not** imply statistical independence in general; it does for jointly Gaussian variables.

## Learn the Concepts

### Algebraic meaning

The dot product multiplies corresponding coordinates and sums them:
$$
u^Tv=u_1v_1+\cdots+u_nv_n.
$$

It measures alignment.

### Geometric meaning

For nonzero vectors,
$$
\cos\theta=\frac{u^Tv}{\|u\|\|v\|}.
$$

Therefore:

- $u^Tv>0$: acute angle.
- $u^Tv=0$: orthogonal.
- $u^Tv<0$: obtuse angle.

The zero-vector case is special because its angle is undefined, even though its dot product with every vector is zero.

### Projection derivation

The closest point to $u$ on the line spanned by $v$ must have the form $cv$.

At the closest point, the residual is perpendicular to the line:
$$
v^T(u-cv)=0.
$$

Expanding:
$$
v^Tu-cv^Tv=0,
$$
hence
$$
c=\frac{v^Tu}{v^Tv}.
$$

So
$$
\operatorname{proj}_v(u)
=
\frac{v^Tu}{\|v\|^2}v.
$$

If $v$ is unit length, this simplifies to
$$
(u^Tv)v.
$$

### Connection to least squares

Least squares generalizes this one-dimensional projection to projection onto an entire column space. At the optimum, the residual is orthogonal to every column of the design matrix.

### Dot product versus independence

If centered sample vectors $x$ and $y$ satisfy
$$
x^Ty=0,
$$
their sample covariance is zero up to normalization by $n$ or $n-1$.

But nonlinear dependence can remain. Uncorrelated does not mean independent unless additional distributional structure, such as joint Gaussianity, is present.

## Required / Important Follow-ups

### Why does projection use $v^Tv$ in the denominator?

Because $v$ may not be unit length. The denominator removes the effect of the basis vector's scale.

### What happens if $v=0$?

Projection onto the span of the zero vector is not defined by the formula because $v^Tv=0$.

### How does this connect to cosine similarity?

Cosine similarity normalizes the dot product by both vector norms and therefore measures direction alignment rather than raw magnitude.
