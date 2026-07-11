"""Unit tests for the exceptional-algebra layer.

This module was published untested as a loose top-level ``py-module``. Now that
it has graduated into the package (issue #13), it earns coverage: the package is
what has graduated, and graduated code is tested.

The headline claims are the dimensions of the exceptional Lie algebras that act
as derivation algebras, plus the F4-invariance and Peirce structure of the
Albert-algebra determinant.
"""

import numpy as np
import pytest

from topographo.core import cayley_dickson_table
from topographo.exceptional import lab
from topographo.exceptional.lab import Albert, defect_matrix, derivations, relative_nullity


@pytest.fixture(scope="module")
def albert():
    return Albert()


def test_uses_core_cayley_dickson_table():
    """The lab must reuse the core structure tensor, not a private copy."""
    assert lab.cayley_dickson_table is cayley_dickson_table


def test_octonion_derivations_span_g2():
    """dim Der(O) = dim g2 = 14."""
    dim, _ = relative_nullity(defect_matrix(cayley_dickson_table(8)))
    assert dim == 14


def test_albert_derivations_span_f4(albert):
    """dim Der(J3(O)) = dim f4 = 52."""
    dim, _ = relative_nullity(defect_matrix(albert.mu))
    assert dim == 52


def test_determinant_matches_classical_diagonal(albert):
    """The cubic form reduces to the ordinary determinant on diagonals."""
    X = np.array([2, 3, 5] + [0] * 24, float)
    assert albert.det(X) == pytest.approx(30.0)


def test_derivations_annihilate_determinant(albert):
    """F4 = Der(J3(O)) preserves the cubic determinant."""
    Der = derivations(albert.mu)
    rng = np.random.default_rng(1)
    eps = 1e-5
    worst = 0.0
    for _ in range(20):
        X = rng.standard_normal(27)
        D = Der[rng.integers(len(Der))]
        worst = max(worst, abs((albert.det(X + eps * (D @ X)) - albert.det(X - eps * (D @ X))) / (2 * eps)))
    assert worst < 1e-4


def test_determinant_is_indefinite_on_trace_sphere(albert):
    """The F4 'crack': det changes sign on the unit trace-hypersphere."""
    G = albert.trace_form()
    L = np.linalg.cholesky(G)
    rng = np.random.default_rng(0)
    vals = np.empty(2000)
    for i in range(vals.size):
        v = np.linalg.solve(L.T, rng.standard_normal(27))
        v /= np.sqrt(v @ G @ v)
        vals[i] = albert.det(v)
    assert vals.min() < 0 < vals.max()
