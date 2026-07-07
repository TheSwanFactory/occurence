"""Validated Cayley-Dickson algebra operators."""

from __future__ import annotations

from itertools import combinations

import numpy as np

from topographo.core.cayley_dickson import cayley_dickson_table


class CayleyDicksonAlgebra:
    """Finite-dimensional real Cayley-Dickson algebra with operator helpers."""

    def __init__(self, dim: int = 16, *, seed: int | None = 42):
        self.dim = dim
        self.C = cayley_dickson_table(dim)
        self.e = np.eye(dim)
        self.rng = np.random.default_rng(seed)

    def mul(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Multiply two vectors in the algebra."""
        return np.einsum("i,j,ijk->k", x, y, self.C)

    def left_operator(self, x: np.ndarray) -> np.ndarray:
        """Left multiplication operator L_x."""
        return np.einsum("i,ijk->kj", x, self.C)

    def right_operator(self, x: np.ndarray) -> np.ndarray:
        """Right multiplication operator R_x."""
        return np.einsum("j,ijk->ki", x, self.C)

    def metric_operator(self, x: np.ndarray) -> np.ndarray:
        """Return M_x = L_x.T L_x."""
        left = self.left_operator(x)
        return left.T @ left

    def alternator(self, x: np.ndarray) -> np.ndarray:
        """Return T_x = L_{x^2} - L_x^2."""
        left = self.left_operator(x)
        return self.left_operator(self.mul(x, x)) - left @ left

    def stepv(self, states: np.ndarray, events: np.ndarray) -> np.ndarray:
        """Vectorized left-settlement step events * states."""
        event_tables = np.einsum("ni,ijk->njk", events, self.C)
        return np.einsum("njk,nj->nk", event_tables, states)

    def conjugate(self, x: np.ndarray) -> np.ndarray:
        """Cayley-Dickson conjugation."""
        return np.concatenate([[x[0]], -x[1:]])

    def sample_basis_zero_divisors(self, n: int) -> np.ndarray:
        """Sample from basis-form unit zero divisors in this algebra."""
        zero_divisors = []
        for i, j in combinations(range(1, self.dim), 2):
            for sign in (1, -1):
                u = (self.e[i] + sign * self.e[j]) / np.sqrt(2)
                singular_values = np.linalg.svd(self.left_operator(u), compute_uv=False)
                if singular_values[-1] < 1e-9:
                    zero_divisors.append(u)
        if not zero_divisors:
            raise ValueError("no basis-form zero divisors found")
        samples = np.array(zero_divisors)
        return samples[self.rng.integers(0, len(samples), n)]

    def sample_pure_pair(self, n: int) -> np.ndarray:
        """Sample random unit pure-pair events for the sedenion crack model."""
        if self.dim != 16:
            raise ValueError("pure-pair sampling is currently defined for dim=16")
        a = self.rng.standard_normal((n, 8))
        a[:, 0] = 0
        a /= np.linalg.norm(a, axis=1, keepdims=True)
        b = self.rng.standard_normal((n, 8))
        b[:, 0] = 0
        b -= np.sum(b * a, axis=1, keepdims=True) * a
        b /= np.linalg.norm(b, axis=1, keepdims=True)
        return np.concatenate([a, b], axis=1) / np.sqrt(2)

    # Backward-compatible aliases used by the current audit script.
    Lop = left_operator
    Rop = right_operator
    sample_crack = sample_basis_zero_divisors
