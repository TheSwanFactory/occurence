"""Exceptional-algebra layer: the 27-dimensional Albert algebra J3(O) and its
F4/G2 structure.

This subpackage is generic exceptional-algebra mathematics (Albert algebra,
F4/G2 decomposition, Peirce/Hessian analysis, determinant invariants,
anisotropy). It is not Occurrence-Theory-specific; it belongs to the reusable
`topographo` library alongside `core` and `ssd`.

It reuses `topographo.core.cayley_dickson_table` as the single source of truth
for the Cayley-Dickson structure tensor.
"""

from topographo.core import cayley_dickson_table
from topographo.exceptional.lab import (
    Albert,
    albert_f4,
    albert_g2_decomposition,
    crack_the_sphere,
    defect_matrix,
    derivations,
    determinant_checks,
    main,
    octonion_anisotropy,
    octonion_g2,
    peirce_and_hessian,
    relative_nullity,
)

__all__ = [
    "Albert",
    "albert_f4",
    "albert_g2_decomposition",
    "cayley_dickson_table",
    "crack_the_sphere",
    "defect_matrix",
    "derivations",
    "determinant_checks",
    "main",
    "octonion_anisotropy",
    "octonion_g2",
    "peirce_and_hessian",
    "relative_nullity",
]
