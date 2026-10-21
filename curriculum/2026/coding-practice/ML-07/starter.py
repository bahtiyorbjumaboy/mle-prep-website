import numpy as np


def sample_negatives(
    interactions: list[tuple[int, int]],
    n_items: int,
    n_neg: int,
    seed: int,
    popularity: np.ndarray | None = None,
) -> np.ndarray:
    """Negative item ids for every positive (user, item) interaction.

    Canonical prompt: given positive user-item interactions and a large catalog,
    generate deterministic negatives using uniform and popularity-weighted sampling
    while excluding known positives.

    Contract:
    - Row `r` of the output holds `n_neg` negatives for `interactions[r]`'s user.
      A negative is never ANY known positive of that user (all of the user's
      interactions, not just the item in row `r`).
    - Within a row, negatives are distinct (sampling without replacement); different
      rows may repeat items.
    - `popularity=None`: uniform over the user's allowed items. Otherwise each draw
      picks an allowed, not-yet-chosen item with probability proportional to
      `popularity[item]`; zero-popularity items are never drawn.
    - All randomness comes from one `np.random.default_rng(seed)`: same inputs and seed
      give identical output.
    - Resources: for a large catalog with uniform sampling, do not build per-user
      O(n_items) arrays (rejection sampling makes the expected cost about
      O(P * n_neg)); the popularity sampler may do an O(n_items) setup once. Users who
      have interacted with most of the catalog must still finish (fall back to
      sampling from the explicit complement when rejection would be slow).

    Args:
        interactions: `(user, item)` pairs; items in `[0, n_items)`; pairs may repeat.
        n_items: catalog size. n_neg: negatives per interaction, `>= 1`.
        seed: RNG seed. popularity: optional `(n_items,)` non-negative finite weights.

    Returns:
        Integer array `(len(interactions), n_neg)`.

    Raises:
        ValueError: if an item id is out of range, `n_neg < 1`, popularity is invalid
            (wrong shape, negative, non-finite), or some user has fewer than `n_neg`
            eligible negatives (items that are not positives and, when weighted, have
            positive popularity).
    """
    raise NotImplementedError("TODO: implement ML-07")
