---
type: interview-answer
item: "2026:bank01:A9"
title: "L1, L2, and L-Infinity Geometry"
created: "2026-09-21"
updated: "2026-09-21"
tags:
  - linear-algebra
  - regularization
  - l1
  - l2
  - sparsity
---

## Canonical Interview Question

Compare the L1, L2, and L∞ unit balls geometrically, then explain why L1 regularization produces exactly zero coefficients while L2 does not. Give me the geometric argument first, then tell me what is happening to the penalty's derivative at zero that makes it possible.

## Mastery Answer

In two dimensions, the $L_2$ unit ball is a filled Euclidean disk with a smooth circular boundary. The $L_1$ unit ball is a diamond, whose corners lie on the coordinate axes. The $L_\infty$ unit ball is an axis-aligned square; in higher dimensions these become a sphere/ball, a cross-polytope, and a hypercube respectively.

The geometric sparsity argument comes from writing regularization in constrained form: minimize the loss subject to the coefficient vector lying inside a norm ball. The optimizer occurs where a loss contour first touches the feasible region.

For $L_1$, the feasible set has corners on the coordinate axes. A nontrivial range of loss-contour orientations first touches one of those corners. At such a corner, one or more coordinates are exactly zero, so $L_1$ frequently produces sparse solutions.

For $L_2$, the boundary is smooth. A generic tangency occurs away from the axes, so coefficients are continuously shrunk but are not normally driven exactly to zero.

The optimization view gives the same conclusion. For one coefficient $\beta$:

$$
\frac{d}{d\beta}\beta^2=2\beta,
$$

so the $L_2$ penalty gradient goes to zero as $\beta\to0$. There is no threshold region that pins the coefficient exactly at zero.

For $L_1$,

$$
\frac{d}{d\beta}|\beta|=
\begin{cases}
+1,&\beta>0,\\
-1,&\beta<0.
\end{cases}
$$

At zero, $|\beta|$ is non-differentiable and has subgradient

$$
\partial |\beta|\big|_{\beta=0}=[-1,1].
$$

With penalty weight $\lambda$, zero satisfies the first-order optimality condition whenever the loss gradient at zero falls inside $[-\lambda,\lambda]$. That creates a genuine interval of gradients for which the exact optimum is $\beta=0$.

This mechanism appears explicitly in soft-thresholding:

$$
S_\lambda(z)
=\operatorname{sign}(z)\max(|z|-\lambda,0).
$$

Soft-thresholding is the exact proximal operator for the $L_1$ penalty and gives the closed-form coefficient update in special geometries such as orthonormal designs. For a general correlated Lasso problem, the coefficients are coupled through the loss, so this scalar formula is not a single global closed-form solution, though coordinate-descent updates use the same thresholding mechanism.

The $L_\infty$ norm constrains the largest absolute coefficient. Its geometry does not place corners on the coordinate axes in the same sparsity-producing way, so it is more naturally associated with capping or equalizing maximum magnitude than with sparse feature selection. $L_\infty$ balls also appear naturally in bounded-perturbation settings such as adversarial robustness.

## Learn the Concepts

### 1. The three norms

For $\beta\in\mathbb{R}^d$:

$$
\|\beta\|_1=\sum_i |\beta_i|,
$$

$$
\|\beta\|_2=\sqrt{\sum_i\beta_i^2},
$$

and

$$
\|\beta\|_\infty=\max_i|\beta_i|.
$$

A unit ball is the set of vectors whose norm is at most one.

In 2D:

- $L_1$: diamond;
- $L_2$: disk;
- $L_\infty$: square.

The location of corners matters more than the visual shape alone.

### 2. Penalized and constrained regularization are two views of the same trade-off

A penalized problem such as

$$
\min_\beta L(\beta)+\lambda\|\beta\|_1
$$

corresponds, under standard convex conditions, to a constrained problem of the form

$$
\min_\beta L(\beta)
\quad\text{subject to}\quad
\|\beta\|_1\le t
$$

for an appropriate relationship between $\lambda$ and $t$.

This constrained view makes the geometry visible: the loss contours expand until they first touch the feasible set.

### 3. Why $L_1$ corners produce sparsity

The $L_1$ ball has corners where many coordinates are zero. In two dimensions, the corners are $(\pm1,0)$ and $(0,\pm1)$.

Because a corner has a range of supporting hyperplanes rather than one unique tangent, many different loss-gradient directions are compatible with an optimum at that same corner. Therefore exact axis contact is not a measure-zero accident; it happens robustly over a range of problems.

That is the geometric reason Lasso solutions are often sparse.

### 4. Why $L_2$ usually shrinks without zeroing

The $L_2$ boundary is differentiable everywhere away from the origin. At a generic optimum, the loss contour has a unique tangent to the smooth sphere. There is no geometrically preferred set of axis-aligned corners, so exact zero coordinates are not normally produced.

This does not mean an $L_2$-regularized coefficient can never be zero. Special symmetry or data conditions can make that happen. The point is that $L_2$ does not have a structural thresholding mechanism that generically creates sparsity.

### 5. Subgradients explain the same phenomenon analytically

For Lasso,

$$
\min_\beta L(\beta)+\lambda|\beta|,
$$

zero is optimal if

$$
0\in \nabla L(0)+\lambda[-1,1].
$$

Equivalently,

$$
|\nabla L(0)|\le\lambda.
$$

So a whole interval of loss gradients maps to the exact same coefficient value, zero.

For ridge,

$$
\nabla\big(\lambda\beta^2\big)=2\lambda\beta.
$$

As $\beta$ approaches zero, the penalty force also approaches zero. Ridge therefore pulls continuously toward zero rather than creating a dead zone around it.

### 6. Soft-thresholding

The proximal problem

$$
\min_\beta \frac12(\beta-z)^2+\lambda|\beta|
$$

has solution

$$
\beta^*=\operatorname{sign}(z)\max(|z|-\lambda,0).
$$

This is soft-thresholding:

- if $|z|\le\lambda$, the solution is exactly zero;
- if $|z|>\lambda$, the solution is shrunk toward zero by $\lambda$.

For orthonormal-design Lasso, the problem decouples by coordinate and this formula directly gives the coefficients. For correlated features, the coordinates interact, so iterative methods such as coordinate descent repeatedly apply conditional thresholding updates.

### 7. What $L_\infty$ regularization does geometrically

The $L_\infty$ constraint

$$
\|\beta\|_\infty\le t
$$

means every coefficient satisfies $|\beta_i|\le t$. The constraint directly caps the largest magnitude.

Its corners occur when multiple coefficients simultaneously hit the maximum magnitude, not when many coefficients vanish. So the geometry favors magnitude equalization/capping rather than sparsity.

### 8. Broader modeling trade-offs

$L_1$ is attractive when sparse feature selection is useful, but with strongly correlated predictors it can choose one feature somewhat arbitrarily among a group.

$L_2$ is stable under correlated features and spreads weight across them, but it does not perform feature selection.

This motivates elastic net, which combines $L_1$ and $L_2$ when both sparsity and grouped stability are desirable.

## Required / Important Follow-ups

### Does soft-thresholding solve arbitrary Lasso in one closed-form step?

No. It is the exact proximal operator for the $L_1$ penalty and gives a direct closed form when the regression geometry decouples, such as an orthonormal design. In a general correlated design, coefficients interact through the loss, although coordinate-descent updates use soft-thresholding conditionally.

### Why does the $L_1$ subgradient create an exact zero?

At zero,

$$
\partial(\lambda|\beta|)=[-\lambda,\lambda].
$$

If the negative loss gradient lies anywhere inside that interval, the first-order optimality condition can be satisfied with $\beta=0$. That interval is the analytic counterpart of the geometric corner.

### What is the main geometric role of $L_\infty$?

$L_\infty$ constrains the maximum coordinate magnitude. Its hypercube geometry tends to cap or equalize large coefficients rather than produce axis-aligned sparsity. It is therefore structurally different from the sparsity-inducing geometry of $L_1$.
