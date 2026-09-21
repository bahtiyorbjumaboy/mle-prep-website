---
type: interview-answer
item: "2026:bank01:B25"
title: "Fundamental Subspaces and Rank-Nullity"
created: "2026-09-21"
updated: "2026-09-21"
tags:
  - linear-algebra
  - subspaces
  - rank-nullity
  - linear-systems
---

## Canonical Interview Question

Name the four fundamental subspaces of a matrix, state the rank-nullity theorem, and connect them to solving a linear system.

## Mastery Answer

For $A\in\mathbb R^{m\times n}$, the four fundamental subspaces are:

- column space $\operatorname{col}(A)\subseteq\mathbb R^m$;
- null space $\operatorname{null}(A)\subseteq\mathbb R^n$;
- row space $\operatorname{row}(A)=\operatorname{col}(A^T)\subseteq\mathbb R^n$;
- left null space $\operatorname{null}(A^T)\subseteq\mathbb R^m$.

They satisfy
$$
\operatorname{row}(A)=\operatorname{null}(A)^\perp
$$
and
$$
\operatorname{col}(A)=\operatorname{null}(A^T)^\perp.
$$

Rank-nullity states
$$
\operatorname{rank}(A)+\operatorname{nullity}(A)=n.
$$

For $Ax=b$, a solution exists iff
$$
b\in\operatorname{col}(A).
$$

If $x_p$ is one particular solution, every solution is
$$
x=x_p+z,\qquad z\in\operatorname{null}(A).
$$

Therefore:

- $b\notin\operatorname{col}(A)$: no exact solution;
- consistent system + trivial null space: exactly one solution;
- consistent system + nontrivial null space: infinitely many solutions.

## Learn the Concepts

### Column space

The column space contains all outputs $Ax$. It therefore determines which right-hand sides $b$ are reachable.

### Null space

The null space contains input directions that the matrix destroys:
$$
Az=0.
$$

These are invisible directions of the transformation.

### Row space

The row space lives in the input space $\mathbb R^n$ and contains the input directions that the rows can detect.

### Left null space

The left null space is
$$
\operatorname{null}(A^T).
$$

It consists of output-space directions orthogonal to every column of $A$.

### Orthogonality relationships

The row space and null space are orthogonal complements in $\mathbb R^n$:
$$
\mathbb R^n
=
\operatorname{row}(A)\oplus\operatorname{null}(A).
$$

Similarly,
$$
\mathbb R^m
=
\operatorname{col}(A)\oplus\operatorname{null}(A^T).
$$

### Rank-nullity

If $A$ has $n$ columns,
$$
\operatorname{rank}(A)+\dim(\operatorname{null}(A))=n.
$$

The $n$ input dimensions split into directions that affect the output and directions that are annihilated.

### Solution geometry

Suppose
$$
Ax_p=b.
$$

For any
$$
z\in\operatorname{null}(A),
$$
we have
$$
A(x_p+z)=Ax_p+Az=b.
$$

Conversely, if $x_1$ and $x_2$ are both solutions, then
$$
A(x_1-x_2)=0,
$$
so their difference lies in the null space.

Thus the complete solution set is an affine translate of the null space.

## Required / Important Follow-ups

### Does rank deficiency always imply infinitely many solutions?

No. Rank deficiency gives a nontrivial null space only relative to the number of columns. There are infinitely many solutions only if the system is also consistent.

### What exactly gives uniqueness?

For a consistent system, uniqueness is equivalent to
$$
\operatorname{null}(A)=\{0\},
$$
which is equivalent to full column rank.

### Why call $x_p$ a particular solution rather than a unique solution?

Because if the null space is nontrivial, $x_p$ is only one representative from an entire affine family $x_p+\operatorname{null}(A)$.
