"""Core algebra primitives for Topographo."""

from topographo.core.algebra import CayleyDicksonAlgebra
from topographo.core.cayley_dickson import cayley_dickson_table
from topographo.core.gates import GateResult, verify_gates

__all__ = [
    "CayleyDicksonAlgebra",
    "GateResult",
    "cayley_dickson_table",
    "verify_gates",
]
