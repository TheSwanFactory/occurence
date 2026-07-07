"""Topographo: reusable computational tools for topographical algebra.

Topographo packages the executable mathematical core behind the Occurrence
Theory research notes. The package is intentionally narrower than the paper:
it provides reusable Cayley-Dickson algebra, validation, and sedenion
settlement helpers without importing the Occurrence Theory narrative layer or
running any audit output at import time.

The central mathematical object in the paper is **Sedenion Settlement
Dynamics** (SSD). SSD studies the 16-dimensional Cayley-Dickson algebra, its
unit zero-divisor locus, and operators built from left multiplication:

- `L_x`: left multiplication by an algebra element.
- `M_x = L_x.T @ L_x`: the metric operator measuring norm transport.
- `T_x = L_{x^2} - L_x^2`: the alternator used to express settlement strain.

The reusable TGT/SSD layer is separated from the interpretive Occurrence
Theory layer. In package terms:

- `topographo.core` contains Cayley-Dickson construction, multiplication
  operators, and mandatory validation gates.
- `topographo.ssd` contains the sedenion-specific wrapper and small channel
  diagnostics used by the settlement audit.
- `occurrence_theory_audit` remains the report-style command-line consumer.

The validation gates are deliberately conservative. Any independent
implementation should pass composition, antisymmetry, quadratic, and Moufang
checks before its numerical certificates are trusted.

Typical use:

```python
from topographo.core import CayleyDicksonAlgebra, verify_gates
from topographo.ssd import SedenionAlgebra, average_metric_operator

assert all(result.passed for result in verify_gates())

algebra = SedenionAlgebra()
events = algebra.sample_crack(84)
mean_metric = average_metric_operator(algebra, events)
```

For the full paper-style audit, use the console command:

```bash
occurrence-theory-audit
```
"""

from topographo.core import CayleyDicksonAlgebra, GateResult, cayley_dickson_table, verify_gates

__all__ = [
    "CayleyDicksonAlgebra",
    "GateResult",
    "cayley_dickson_table",
    "verify_gates",
]
