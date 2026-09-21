---
type: interview-answer
item: "2026:bank01:A12"
title: "Backpropagation Through a Two-Layer Network"
created: "2026-09-21"
updated: "2026-09-21"
tags:
  - linear-algebra
  - backpropagation
  - neural-networks
  - matrix-calculus
---

## Canonical Interview Question

Take a two-layer network: z₁ = W₁x + b₁, a₁ = φ(z₁), z₂ = W₂a₁ + b₂, scalar loss L. Derive the gradients with respect to W₁, W₂, b₁, and b₂. I care about the shapes and about *why* each transpose, each elementwise product, and each sum appears — not just the final expressions. Then tell me what happens to the weight gradient when you batch.

## Mastery Answer

Let
$$
\delta_2=\frac{\partial L}{\partial z_2}.
$$

For the second linear layer,
$$
\frac{\partial L}{\partial W_2}
=
\delta_2 a_1^T,
\qquad
\frac{\partial L}{\partial b_2}
=
\delta_2.
$$

The weight gradient is an **outer product**: downstream error times layer input. The transpose is required to produce the shape of $W_2$.

Backpropagating through the linear map and then the activation gives
$$
\delta_1
=
(W_2^T\delta_2)\odot \phi'(z_1).
$$

$W_2^T$ transports the gradient from output space back into hidden space. The Hadamard product appears because $\phi$ is applied elementwise, so its Jacobian is diagonal.

Then
$$
\frac{\partial L}{\partial W_1}
=
\delta_1x^T,
\qquad
\frac{\partial L}{\partial b_1}
=
\delta_1.
$$

For a batch with examples stored as columns,
$$
\frac{\partial L}{\partial W_2}
=
\Delta_2A_1^T,
\qquad
\frac{\partial L}{\partial W_1}
=
\Delta_1X^T.
$$

These matrix products sum the per-example outer products. Bias gradients sum across examples because the same bias vector is reused for every example. If the batch loss is an average rather than a sum, the aggregate gradients carry the corresponding factor $1/B$.

## Learn the Concepts

### Shapes

Let

$$
x\in\mathbb R^d,
\qquad
W_1\in\mathbb R^{h\times d},
\qquad
b_1,z_1,a_1\in\mathbb R^h,
$$

and

$$
W_2\in\mathbb R^{k\times h},
\qquad
b_2,z_2,\delta_2\in\mathbb R^k.
$$

The scalar loss is $L$.

### Second-layer weight gradient

For one coordinate,
$$
z_{2,i}
=
\sum_j W_{2,ij}a_{1,j}+b_{2,i}.
$$

Therefore
$$
\frac{\partial L}{\partial W_{2,ij}}
=
\frac{\partial L}{\partial z_{2,i}}
\frac{\partial z_{2,i}}{\partial W_{2,ij}}
=
\delta_{2,i}a_{1,j}.
$$

Collecting all entries gives
$$
\frac{\partial L}{\partial W_2}
=
\delta_2a_1^T.
$$

Shape:
$$
(k\times 1)(1\times h)=k\times h.
$$

### Why $W_2^T$ appears

Forward propagation uses
$$
z_2=W_2a_1+b_2,
$$
which maps
$$
\mathbb R^h\to\mathbb R^k.
$$

The gradient must be transported in the reverse direction:
$$
\frac{\partial L}{\partial a_1}
=
W_2^T\delta_2
\in\mathbb R^h.
$$

The transpose is the adjoint of the forward linear map under the standard Euclidean inner product.

### Why the activation derivative is elementwise

Since
$$
a_1=\phi(z_1)
$$
coordinatewise,
$$
a_{1,i}=\phi(z_{1,i}),
$$
the Jacobian is diagonal:
$$
J_\phi(z_1)=\operatorname{diag}(\phi'(z_1)).
$$

Multiplying by this diagonal Jacobian is equivalent to the Hadamard product:
$$
\delta_1
=
(W_2^T\delta_2)\odot\phi'(z_1).
$$

The factor must be $\phi'(z_1)$, not $\phi(z_1)$, because backpropagation applies the chain rule through the activation.

### First-layer gradients

Once $\delta_1$ is known, the first layer repeats the same pattern:
$$
\frac{\partial L}{\partial W_1}
=
\delta_1x^T,
$$
$$
\frac{\partial L}{\partial b_1}
=
\delta_1.
$$

The reusable mental rule is:

- weight gradient = error $\times$ input$^T$;
- previous-activation gradient = $W^T\times$ error;
- activation backward = upstream gradient $\odot$ local derivative.

### Batching

With examples as columns,
$$
X\in\mathbb R^{d\times B},
\qquad
A_1\in\mathbb R^{h\times B},
\qquad
\Delta_2\in\mathbb R^{k\times B}.
$$

Then
$$
\Delta_2A_1^T
=
\sum_{n=1}^B
\delta_2^{(n)}a_1^{(n)T}.
$$

So matrix multiplication is simply the vectorized sum of per-example outer products.

Biases are shared across all examples, so their gradients aggregate over the batch dimension.

## Required / Important Follow-ups

### Why is the weight gradient an outer product?

Each weight connects one input coordinate to one output coordinate. The derivative for entry $(i,j)$ is exactly downstream error coordinate $i$ times input coordinate $j$.

### Why is $\phi'(z_1)$ used rather than $\phi(z_1)$?

Because the chain rule multiplies by the **local derivative** of the activation. The forward activation value and the derivative are different objects.

### Why is the product Hadamard rather than a dot product?

Each activation coordinate depends only on its matching preactivation coordinate. The Jacobian is diagonal, so multiplying by it is equivalent to coordinatewise multiplication.

### What changes if the batch is stored as rows instead of columns?

The same mathematics holds, but transpose locations change with the layout convention. The invariant is still: aggregate the per-example outer products and sum shared-parameter contributions across the batch dimension.
